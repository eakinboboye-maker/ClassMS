import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.jupyterlite import LessonLaunchConfig
from app.schemas.jupyterlite import LessonLaunchConfigCreate, LessonLaunchConfigUpdate

router = APIRouter()


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
        is_active=payload.is_active,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "id": row.id,
        "lesson_slug": row.lesson_slug,
        "course_code": row.course_code,
        "title": row.title,
        "assessment_id": row.assessment_id,
        "attendance_session_id": row.attendance_session_id,
        "question_keys": json.loads(row.question_keys_json or "{}"),
        "notebook_path": row.notebook_path,
        "is_active": row.is_active,
    }


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
    if payload.is_active is not None:
        row.is_active = payload.is_active

    db.commit()
    db.refresh(row)

    return {
        "id": row.id,
        "lesson_slug": row.lesson_slug,
        "course_code": row.course_code,
        "title": row.title,
        "assessment_id": row.assessment_id,
        "attendance_session_id": row.attendance_session_id,
        "question_keys": json.loads(row.question_keys_json or "{}"),
        "notebook_path": row.notebook_path,
        "is_active": row.is_active,
    }


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

    return {
        "lesson_slug": row.lesson_slug,
        "course_code": row.course_code,
        "title": row.title,
        "assessment_id": row.assessment_id,
        "attendance_session_id": row.attendance_session_id,
        "question_keys": json.loads(row.question_keys_json or "{}"),
        "notebook_path": row.notebook_path,
    }
