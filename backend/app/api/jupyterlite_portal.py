import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.jupyterlite import LessonLaunchConfig
from app.models.assessment import Assessment, Attempt
from app.models.response import Response
from app.models.grading import Score
from app.models.attendance import AttendanceRecord
from app.schemas.jupyterlite import (
    LessonLaunchConfigCreate,
    LessonLaunchConfigUpdate,
    AttendanceWindowRead,
    PortalLessonRead,
    PortalHomeResponse,
)
from app.services.autosave_service import save_response, finalize_attempt, get_attempt_responses

router = APIRouter()


def _score_summary(db: Session, attempt_id: int) -> tuple[float, float]:
    scores = db.query(Score).filter(Score.attempt_id == attempt_id).all()
    return (
        float(sum(s.awarded_marks for s in scores)),
        float(sum(s.max_marks for s in scores)),
    )


def _attendance_status_for_user(db: Session, lesson: LessonLaunchConfig, user_id: int) -> AttendanceWindowRead | None:
    if not lesson.attendance_session_id:
        return None

    now = datetime.utcnow()
    already = db.query(AttendanceRecord).filter(
        AttendanceRecord.attendance_session_id == lesson.attendance_session_id,
        AttendanceRecord.user_id == user_id,
    ).first()

    is_open_now = True
    if lesson.attendance_open_at and now < lesson.attendance_open_at:
        is_open_now = False
    if lesson.attendance_close_at and now > lesson.attendance_close_at:
        is_open_now = False

    return AttendanceWindowRead(
        lesson_slug=lesson.lesson_slug,
        attendance_open_at=lesson.attendance_open_at,
        attendance_close_at=lesson.attendance_close_at,
        is_open_now=is_open_now,
        already_marked=already is not None,
    )


def _serialize_config(row: LessonLaunchConfig) -> dict:
    return {
        "lesson_slug": row.lesson_slug,
        "course_code": row.course_code,
        "title": row.title,
        "assessment_id": row.assessment_id,
        "attendance_session_id": row.attendance_session_id,
        "question_keys": json.loads(row.question_keys_json or "{}"),
        "notebook_path": row.notebook_path,
        "attendance_open_at": row.attendance_open_at.isoformat() if row.attendance_open_at else None,
        "attendance_close_at": row.attendance_close_at.isoformat() if row.attendance_close_at else None,
        "show_on_portal": row.show_on_portal,
        "allow_portal_mock_exam": row.allow_portal_mock_exam,
        "is_active": row.is_active,
    }


@router.post("/lesson-config")
def create_lesson_launch_config(
    payload: LessonLaunchConfigCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    existing = db.query(LessonLaunchConfig).filter(
        LessonLaunchConfig.lesson_slug == payload.lesson_slug
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="lesson_slug already exists")

    row = LessonLaunchConfig(
        lesson_slug=payload.lesson_slug,
        course_code=payload.course_code,
        title=payload.title,
        assessment_id=payload.assessment_id,
        attendance_session_id=payload.attendance_session_id,
        question_keys_json=json.dumps(payload.question_keys),
        notebook_path=payload.notebook_path,
        attendance_open_at=payload.attendance_open_at,
        attendance_close_at=payload.attendance_close_at,
        show_on_portal=payload.show_on_portal,
        allow_portal_mock_exam=payload.allow_portal_mock_exam,
        is_active=payload.is_active,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize_config(row)


@router.put("/lesson-config/{lesson_slug}")
def update_lesson_launch_config(
    lesson_slug: str,
    payload: LessonLaunchConfigUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    row = db.query(LessonLaunchConfig).filter(
        LessonLaunchConfig.lesson_slug == lesson_slug
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Lesson config not found")

    if payload.title is not None:
        row.title = payload.title
    if payload.assessment_id is not None:
        row.assessment_id = payload.assessment_id
    if payload.attendance_session_id is not None:
        row.attendance_session_id = payload.attendance_session_id
    if payload.question_keys is not None:
        row.question_keys_json = json.dumps(payload.question_keys)
    if payload.notebook_path is not None:
        row.notebook_path = payload.notebook_path
    if payload.attendance_open_at is not None:
        row.attendance_open_at = payload.attendance_open_at
    if payload.attendance_close_at is not None:
        row.attendance_close_at = payload.attendance_close_at
    if payload.show_on_portal is not None:
        row.show_on_portal = payload.show_on_portal
    if payload.allow_portal_mock_exam is not None:
        row.allow_portal_mock_exam = payload.allow_portal_mock_exam
    if payload.is_active is not None:
        row.is_active = payload.is_active

    db.commit()
    db.refresh(row)
    return _serialize_config(row)


@router.get("/lesson-config/{lesson_slug}")
def get_lesson_launch_config(
    lesson_slug: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    row = db.query(LessonLaunchConfig).filter(
        LessonLaunchConfig.lesson_slug == lesson_slug,
        LessonLaunchConfig.is_active.is_(True),
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Lesson config not found")
    return _serialize_config(row)


@router.get("/portal/home", response_model=PortalHomeResponse)
def portal_home(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.query(LessonLaunchConfig).filter(
        LessonLaunchConfig.is_active.is_(True),
        LessonLaunchConfig.show_on_portal.is_(True),
    ).order_by(LessonLaunchConfig.lesson_slug.asc()).all()

    lessons = []
    mock_exams = []

    for row in rows:
        attendance = _attendance_status_for_user(db, row, current_user.id)
        lessons.append(
            PortalLessonRead(
                lesson_slug=row.lesson_slug,
                title=row.title,
                course_code=row.course_code,
                notebook_path=row.notebook_path,
                attendance=attendance,
            )
        )
        if row.allow_portal_mock_exam:
            mock_exams.append(
                {
                    "lesson_slug": row.lesson_slug,
                    "title": row.title,
                    "course_code": row.course_code,
                }
            )

    attempts = db.query(Attempt, Assessment).join(
        Assessment, Assessment.id == Attempt.assessment_id
    ).filter(
        Attempt.user_id == current_user.id,
        Attempt.status == "submitted",
    ).order_by(Attempt.submitted_at.asc()).all()

    perf_items = []
    for attempt, assessment in attempts:
        total_awarded, total_max = _score_summary(db, attempt.id)
        percent = (total_awarded / total_max * 100.0) if total_max else 0.0
        perf_items.append(
            {
                "attempt_id": attempt.id,
                "assessment_id": assessment.id,
                "assessment_title": assessment.title,
                "assessment_type": assessment.type,
                "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                "total_awarded": total_awarded,
                "total_max": total_max,
                "percent": percent,
            }
        )

    return PortalHomeResponse(
        lessons=lessons,
        mock_exams=mock_exams,
        performance={"items": perf_items},
    )


@router.post("/portal/launch/{lesson_slug}")
def portal_launch_lesson(
    lesson_slug: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    row = db.query(LessonLaunchConfig).filter(
        LessonLaunchConfig.lesson_slug == lesson_slug,
        LessonLaunchConfig.is_active.is_(True),
        LessonLaunchConfig.show_on_portal.is_(True),
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not available on portal")
    return _serialize_config(row)


@router.get("/attendance-window/{lesson_slug}", response_model=AttendanceWindowRead)
def get_attendance_window(
    lesson_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(LessonLaunchConfig).filter(
        LessonLaunchConfig.lesson_slug == lesson_slug,
        LessonLaunchConfig.is_active.is_(True),
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Lesson config not found")

    attendance = _attendance_status_for_user(db, row, current_user.id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not configured for lesson")
    return attendance


@router.post("/attendance/{lesson_slug}/mark")
def mark_attendance_for_lesson(
    lesson_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(LessonLaunchConfig).filter(
        LessonLaunchConfig.lesson_slug == lesson_slug,
        LessonLaunchConfig.is_active.is_(True),
    ).first()
    if not row or not row.attendance_session_id:
        raise HTTPException(status_code=404, detail="Attendance not configured for lesson")

    attendance = _attendance_status_for_user(db, row, current_user.id)
    if not attendance.is_open_now:
        raise HTTPException(status_code=400, detail="Attendance is not currently open")
    if attendance.already_marked:
        raise HTTPException(status_code=400, detail="Attendance already marked")

    record = AttendanceRecord(
        attendance_session_id=row.attendance_session_id,
        user_id=current_user.id,
        status="present",
        metadata_json=json.dumps({"marked_from": "portal", "lesson_slug": lesson_slug}),
    )
    db.add(record)
    db.commit()
    return {"status": "marked", "lesson_slug": lesson_slug}


@router.get("/portal/performance")
def portal_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempts = db.query(Attempt, Assessment).join(
        Assessment, Assessment.id == Attempt.assessment_id
    ).filter(
        Attempt.user_id == current_user.id,
        Attempt.status == "submitted",
    ).order_by(Attempt.submitted_at.asc()).all()

    items = []
    for attempt, assessment in attempts:
        total_awarded, total_max = _score_summary(db, attempt.id)
        percent = (total_awarded / total_max * 100.0) if total_max else 0.0
        items.append(
            {
                "attempt_id": attempt.id,
                "assessment_id": assessment.id,
                "assessment_title": assessment.title,
                "assessment_type": assessment.type,
                "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                "total_awarded": total_awarded,
                "total_max": total_max,
                "percent": percent,
            }
        )

    return {"items": items}


@router.post("/portal/mock-exams/{lesson_slug}/start")
def portal_start_mock_exam(
    lesson_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(LessonLaunchConfig).filter(
        LessonLaunchConfig.lesson_slug == lesson_slug,
        LessonLaunchConfig.is_active.is_(True),
        LessonLaunchConfig.allow_portal_mock_exam.is_(True),
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Portal mock exam not found")

    assessment = db.get(Assessment, row.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    existing = db.query(Attempt).filter(
        Attempt.assessment_id == assessment.id,
        Attempt.user_id == current_user.id,
        Attempt.status == "in_progress",
    ).first()
    if existing:
        return {
            "attempt_id": existing.id,
            "assessment_id": assessment.id,
            "status": existing.status,
            "expires_at": existing.expires_at,
        }

    attempt = Attempt(
        assessment_id=assessment.id,
        user_id=current_user.id,
        status="in_progress",
        expires_at=datetime.utcnow(),
        seb_validated=False,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return {
        "attempt_id": attempt.id,
        "assessment_id": assessment.id,
        "status": attempt.status,
        "expires_at": attempt.expires_at,
    }


@router.get("/portal/mock-exams/{attempt_id}/paper")
def portal_mock_exam_paper(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    from app.api.mock_exams import get_mock_exam_paper
    return get_mock_exam_paper(attempt.assessment_id, db, current_user)


@router.post("/portal/mock-exams/{attempt_id}/autosave")
def portal_mock_exam_autosave(
    attempt_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    for item in payload.get("responses", []):
        save_response(db, attempt_id, item["question_id"], item["response"], is_final=False)
    return {"status": "ok"}


@router.post("/portal/mock-exams/{attempt_id}/submit")
def portal_mock_exam_submit(
    attempt_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    finalize_attempt(db, attempt, payload.get("submitted_payload", {}))
    return {"status": "submitted"}


@router.get("/portal/mock-exams/{attempt_id}/results")
def portal_mock_exam_results(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    from app.api.mock_exams import get_mock_exam_results
    return get_mock_exam_results(attempt_id, db, current_user)
