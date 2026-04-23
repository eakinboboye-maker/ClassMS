import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.assessment import Assessment, AssessmentWindow, AssessmentItem, Attempt, AssessmentCandidate
from app.models.question import Question
from app.models.grading import Score
from app.schemas.assessment import AssessmentCreate, AssessmentRead
from app.schemas.security_exam import (
    ExamSessionStartResponse,
    ExamHeartbeatRequest,
    ExamSubmitRequest,
)
from app.schemas.response import AutosavePayload
from app.services.assessment_builder import build_assessment
from app.services.autosave_service import save_response, finalize_attempt, get_attempt_responses
from app.services.objective_grader import grade_mcq_single, grade_mcq_multi
from app.services.fillgap_grader import grade_fill_gap
from app.services.seb_validator import validate_seb_for_assessment
from app.services.exam_session_service import (
    start_exam_session,
    get_active_exam_session,
    validate_exam_session_token,
    rotate_exam_session_nonce,
    invalidate_other_exam_sessions,
    log_replay_incident,
)

router = APIRouter()


def _require_candidate_eligibility(db: Session, assessment_id: int, user_id: int) -> None:
    candidate_count = (
        db.query(AssessmentCandidate)
        .filter(AssessmentCandidate.assessment_id == assessment_id)
        .count()
    )
    if candidate_count == 0:
        return

    allowed = (
        db.query(AssessmentCandidate)
        .filter(
            AssessmentCandidate.assessment_id == assessment_id,
            AssessmentCandidate.user_id == user_id,
        )
        .first()
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="User is not eligible for this assessment")


@router.post("/", response_model=AssessmentRead)
def create_formal_exam(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    payload.type = "formal"
    payload.requires_seb = True
    return build_assessment(db, payload)


@router.post("/{assessment_id}/start", response_model=ExamSessionStartResponse)
def start_formal_exam(
    assessment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessment = db.get(Assessment, assessment_id)
    if not assessment or assessment.type != "formal":
        raise HTTPException(status_code=404, detail="Formal exam not found")

    validate_seb_for_assessment(db, assessment_id, request)
    _require_candidate_eligibility(db, assessment_id, current_user.id)

    final_attempt = (
        db.query(Attempt)
        .filter(
            Attempt.assessment_id == assessment_id,
            Attempt.user_id == current_user.id,
            Attempt.status == "submitted",
        )
        .first()
    )
    if final_attempt:
        raise HTTPException(status_code=400, detail="Final submission already exists")

    window = db.query(AssessmentWindow).filter(AssessmentWindow.assessment_id == assessment_id).first()
    now = datetime.utcnow()
    if not window or now < window.open_time or now > window.close_time:
        raise HTTPException(status_code=400, detail="Exam not currently open")

    existing = db.query(Attempt).filter(
        Attempt.assessment_id == assessment_id,
        Attempt.user_id == current_user.id,
        Attempt.status == "in_progress",
    ).first()

    if existing:
        session = get_active_exam_session(db, existing.id)
        if not session:
            session = start_exam_session(db, existing)
            db.commit()
            db.refresh(existing)
            db.refresh(session)

        invalidate_other_exam_sessions(db, existing.id, session.id)
        return ExamSessionStartResponse(
            attempt_id=existing.id,
            assessment_id=assessment_id,
            expires_at=existing.expires_at.isoformat() if existing.expires_at else None,
            status=existing.status,
            exam_session_token=session.session_token,
            resume_token=existing.resume_token,
        )

    attempt = Attempt(
        assessment_id=assessment_id,
        user_id=current_user.id,
        status="in_progress",
        expires_at=now + timedelta(minutes=assessment.duration_minutes),
        seb_validated=True,
    )
    db.add(attempt)
    db.flush()

    session = start_exam_session(db, attempt)
    db.commit()
    db.refresh(attempt)
    db.refresh(session)

    return ExamSessionStartResponse(
        attempt_id=attempt.id,
        assessment_id=assessment_id,
        expires_at=attempt.expires_at.isoformat() if attempt.expires_at else None,
        status=attempt.status,
        exam_session_token=session.session_token,
        resume_token=attempt.resume_token,
    )


@router.post("/{assessment_id}/resume", response_model=ExamSessionStartResponse)
def resume_formal_exam(
    assessment_id: int,
    request: Request,
    resume_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_seb_for_assessment(db, assessment_id, request)
    _require_candidate_eligibility(db, assessment_id, current_user.id)

    attempt = (
        db.query(Attempt)
        .filter(
            Attempt.assessment_id == assessment_id,
            Attempt.user_id == current_user.id,
            Attempt.status == "in_progress",
            Attempt.resume_token == resume_token,
        )
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="No resumable attempt")

    session = get_active_exam_session(db, attempt.id)
    if not session:
        session = start_exam_session(db, attempt)
        db.commit()
        db.refresh(session)

    invalidate_other_exam_sessions(db, attempt.id, session.id)

    return ExamSessionStartResponse(
        attempt_id=attempt.id,
        assessment_id=attempt.assessment_id,
        expires_at=attempt.expires_at.isoformat() if attempt.expires_at else None,
        status=attempt.status,
        exam_session_token=session.session_token,
        resume_token=attempt.resume_token,
    )


@router.post("/attempts/{attempt_id}/heartbeat")
def heartbeat_formal_exam(
    attempt_id: int,
    payload: ExamHeartbeatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = validate_exam_session_token(db, attempt_id, current_user.id, payload.exam_session_token)

    if payload.nonce and session.session_nonce and payload.nonce != session.session_nonce:
        log_replay_incident(db, attempt_id, {"reason": "nonce_mismatch"})
        raise HTTPException(status_code=403, detail="Invalid session nonce")

    next_nonce = rotate_exam_session_nonce(db, session)
    return {
        "status": "ok",
        "last_seen_at": session.last_seen_at.isoformat(),
        "next_nonce": next_nonce,
    }


@router.get("/{assessment_id}/paper")
def get_formal_exam_paper(
    assessment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items = db.query(AssessmentItem).filter(
        AssessmentItem.assessment_id == assessment_id
    ).order_by(AssessmentItem.order_index).all()

    result = []
    for item in items:
        q = db.get(Question, item.question_id)
        if q.type not in {"mcq_single", "mcq_multi", "fill_gap"}:
            continue
        result.append(
            {
                "question_id": q.id,
                "type": q.type,
                "prompt_md": q.prompt_md,
                "marks": item.points_override or q.marks,
            }
        )
    return {"items": result}


@router.post("/attempts/{attempt_id}/autosave")
def autosave_formal_exam(
    attempt_id: int,
    payload: AutosavePayload,
    exam_session_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    validate_exam_session_token(db, attempt_id, current_user.id, exam_session_token)

    for item in payload.responses:
        save_response(db, attempt_id, item.question_id, item.response, is_final=False)
    return {"status": "ok"}


@router.post("/attempts/{attempt_id}/submit")
def submit_formal_exam(
    attempt_id: int,
    payload: ExamSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.status == "submitted":
        raise HTTPException(status_code=400, detail="Attempt already submitted")

    validate_exam_session_token(db, attempt_id, current_user.id, payload.exam_session_token)

    responses = get_attempt_responses(db, attempt_id)

    for resp in responses:
        question = db.get(Question, resp.question_id)
        response_payload = json.loads(resp.response_json)

        if question.type == "mcq_single":
            awarded, _ = grade_mcq_single(db, question.id, response_payload, question.marks)
        elif question.type == "mcq_multi":
            awarded, _ = grade_mcq_multi(db, question.id, response_payload, question.marks)
        elif question.type == "fill_gap":
            awarded, _ = grade_fill_gap(db, question.id, response_payload)
        else:
            continue

        existing = db.query(Score).filter(
            Score.attempt_id == attempt_id,
            Score.question_id == question.id,
        ).first()
        if not existing:
            db.add(
                Score(
                    attempt_id=attempt_id,
                    question_id=question.id,
                    awarded_marks=awarded,
                    max_marks=question.marks,
                    grading_method=question.type,
                    is_final=True,
                )
            )

    db.commit()
    finalize_attempt(db, attempt, payload.submitted_payload)
    return {"status": "submitted"}
