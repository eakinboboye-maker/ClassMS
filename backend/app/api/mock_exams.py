import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.assessment import Assessment, AssessmentWindow, AssessmentItem, Attempt
from app.models.question import Question, QuestionOption, QuestionGap
from app.models.grading import Score, AIGradingJob
from app.schemas.assessment import AssessmentCreate, AssessmentRead, StartAssessmentResponse
from app.schemas.response import AutosavePayload, FinalSubmitRequest
from app.services.assessment_builder import build_assessment
from app.services.autosave_service import save_response, finalize_attempt, get_attempt_responses
from app.services.objective_grader import grade_mcq_single, grade_mcq_multi
from app.services.fillgap_grader import grade_fill_gap

router = APIRouter()


def _serialize_question_for_paper(db: Session, q: Question, marks: int):
    payload = {
        "question_id": q.id,
        "type": q.type,
        "prompt_md": q.prompt_md,
        "marks": marks,
    }

    if q.type in {"mcq_single", "mcq_multi"}:
        options = (
            db.query(QuestionOption)
            .filter(QuestionOption.question_id == q.id)
            .order_by(QuestionOption.id.asc())
            .all()
        )
        payload["options"] = [{"option_key": opt.option_key, "text": opt.text} for opt in options]

    if q.type == "fill_gap":
        gaps = (
            db.query(QuestionGap)
            .filter(QuestionGap.question_id == q.id)
            .order_by(QuestionGap.position.asc())
            .all()
        )
        payload["gaps"] = [{"gap_key": gap.gap_key, "position": gap.position, "marks": gap.marks} for gap in gaps]

    return payload


@router.post("/", response_model=AssessmentRead)
def create_mock_exam(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    payload.type = "mock"
    payload.requires_seb = False
    return build_assessment(db, payload)


@router.post("/{assessment_id}/start", response_model=StartAssessmentResponse)
def start_mock_exam(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessment = db.get(Assessment, assessment_id)
    if not assessment or assessment.type != "mock":
        raise HTTPException(status_code=404, detail="Mock exam not found")

    window = db.query(AssessmentWindow).filter(AssessmentWindow.assessment_id == assessment_id).first()
    now = datetime.utcnow()
    if not window or now < window.open_time or now > window.close_time:
        raise HTTPException(status_code=400, detail="Mock exam not currently open")

    existing = db.query(Attempt).filter(
        Attempt.assessment_id == assessment_id,
        Attempt.user_id == current_user.id,
        Attempt.status == "in_progress",
    ).first()
    if existing:
        return StartAssessmentResponse(
            attempt_id=existing.id,
            assessment_id=assessment_id,
            expires_at=existing.expires_at,
            status=existing.status,
        )

    attempt = Attempt(
        assessment_id=assessment_id,
        user_id=current_user.id,
        status="in_progress",
        expires_at=now + timedelta(minutes=assessment.duration_minutes),
        seb_validated=False,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return StartAssessmentResponse(
        attempt_id=attempt.id,
        assessment_id=assessment_id,
        expires_at=attempt.expires_at,
        status=attempt.status,
    )


@router.get("/{assessment_id}/paper")
def get_mock_exam_paper(
    assessment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items = db.query(AssessmentItem).filter(
        AssessmentItem.assessment_id == assessment_id
    ).order_by(AssessmentItem.order_index.asc()).all()

    result = []
    for item in items:
        q = db.get(Question, item.question_id)
        if not q:
            continue
        result.append(_serialize_question_for_paper(db, q, item.points_override or q.marks))

    return {"items": result}


@router.post("/attempts/{attempt_id}/autosave")
def autosave_mock_exam(
    attempt_id: int,
    payload: AutosavePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    for item in payload.responses:
        save_response(db, attempt_id, item.question_id, item.response, is_final=False)

    return {"status": "ok"}


@router.post("/attempts/{attempt_id}/submit")
def submit_mock_exam(
    attempt_id: int,
    payload: FinalSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.status == "submitted":
        raise HTTPException(status_code=400, detail="Attempt already submitted")

    responses = get_attempt_responses(db, attempt_id)

    for resp in responses:
        question = db.get(Question, resp.question_id)
        response_payload = json.loads(resp.response_json)

        if question.type == "mcq_single":
            awarded, _ = grade_mcq_single(db, question.id, response_payload, question.marks)
            db.add(Score(attempt_id=attempt_id, question_id=question.id, awarded_marks=awarded, max_marks=question.marks, grading_method=question.type, is_final=True))
        elif question.type == "mcq_multi":
            awarded, _ = grade_mcq_multi(db, question.id, response_payload, question.marks)
            db.add(Score(attempt_id=attempt_id, question_id=question.id, awarded_marks=awarded, max_marks=question.marks, grading_method=question.type, is_final=True))
        elif question.type == "fill_gap":
            awarded, _ = grade_fill_gap(db, question.id, response_payload)
            db.add(Score(attempt_id=attempt_id, question_id=question.id, awarded_marks=awarded, max_marks=question.marks, grading_method=question.type, is_final=True))
        elif question.type in {"short_answer", "essay"}:
            db.add(AIGradingJob(response_id=resp.id, status="queued"))

    db.commit()
    finalize_attempt(db, attempt, payload.submitted_payload)
    return {"status": "submitted"}


@router.get("/attempts/{attempt_id}/scores")
def get_mock_exam_scores(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    scores = db.query(Score).filter(Score.attempt_id == attempt_id).all()
    return {
        "attempt_id": attempt_id,
        "total_awarded": sum(s.awarded_marks for s in scores),
        "total_max": sum(s.max_marks for s in scores),
        "scores": [
            {
                "question_id": s.question_id,
                "awarded_marks": s.awarded_marks,
                "max_marks": s.max_marks,
                "grading_method": s.grading_method,
            }
            for s in scores
        ],
    }
    

@router.get("/attempts/{attempt_id}/results")
def get_mock_exam_results(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    scores = db.query(Score).filter(Score.attempt_id == attempt_id).all()
    score_map = {s.question_id: s for s in scores}

    responses = get_attempt_responses(db, attempt_id)
    items = []

    for resp in responses:
        q = db.get(Question, resp.question_id)
        if not q:
            continue

        score = score_map.get(q.id)
        awarded = score.awarded_marks if score else 0.0
        max_marks = score.max_marks if score else float(q.marks)
        is_correct = awarded >= max_marks and max_marks > 0

        answer_key = json.loads(q.answer_key_json) if q.answer_key_json else {}
        correct_answer_summary = None

        if q.type == "mcq_single":
            options = db.query(QuestionOption).filter(
                QuestionOption.question_id == q.id,
                QuestionOption.is_correct.is_(True),
            ).all()
            correct_answer_summary = [o.option_key for o in options]

        elif q.type == "mcq_multi":
            options = db.query(QuestionOption).filter(
                QuestionOption.question_id == q.id,
                QuestionOption.is_correct.is_(True),
            ).all()
            correct_answer_summary = [o.option_key for o in options]

        elif q.type == "fill_gap":
            gaps = db.query(QuestionGap).filter(QuestionGap.question_id == q.id).all()
            gap_summary = {}
            for gap in gaps:
                accepted = db.query(AcceptedAnswer).filter(AcceptedAnswer.gap_id == gap.id).all()
                gap_summary[gap.gap_key] = [a.text for a in accepted]
            correct_answer_summary = gap_summary

        elif q.type in {"short_answer", "essay"}:
            correct_answer_summary = answer_key.get("canonical_answer")

        items.append(
            {
                "question_id": q.id,
                "type": q.type,
                "prompt_md": q.prompt_md,
                "awarded_marks": awarded,
                "max_marks": max_marks,
                "is_correct": is_correct,
                "grading_method": score.grading_method if score else None,
                "correct_answer_summary": correct_answer_summary,
                "show_explanation_after_submit": q.show_explanation_after_submit,
                "explanation_md": q.explanation_md if q.show_explanation_after_submit else None,
            }
        )

    return {
        "attempt_id": attempt_id,
        "total_awarded": sum(s.awarded_marks for s in scores),
        "total_max": sum(s.max_marks for s in scores),
        "items": items,
    }
