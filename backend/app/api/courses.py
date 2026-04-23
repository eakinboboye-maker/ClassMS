from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.course import Course, Section, Enrollment
from app.models.user import User
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.schemas.course import (
    CourseCreate,
    CourseRead,
    SectionCreate,
    SectionRead,
    EnrollmentCreate,
    AttendanceSessionCreate,
    AttendanceSessionRead,
    AttendanceMarkRequest,
    AttendanceRecordRead,
)

router = APIRouter()


@router.post("/", response_model=CourseRead)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    course = Course(code=payload.code, title=payload.title, description=payload.description)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/", response_model=list[CourseRead])
def list_courses(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor", "student")),
):
    return db.query(Course).all()


@router.post("/sections", response_model=SectionRead)
def create_section(
    payload: SectionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    section = Section(
        course_id=payload.course_id,
        name=payload.name,
        term=payload.term,
        instructor_id=payload.instructor_id,
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


@router.post("/enroll")
def enroll_user(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    enrollment = Enrollment(user_id=payload.user_id, section_id=payload.section_id)
    db.add(enrollment)
    db.commit()
    return {"status": "ok"}


@router.post("/attendance/sessions", response_model=AttendanceSessionRead)
def create_attendance_session(
    payload: AttendanceSessionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    if payload.close_time <= payload.open_time:
        raise HTTPException(status_code=400, detail="close_time must be after open_time")

    session = AttendanceSession(
        section_id=payload.section_id,
        title=payload.title,
        open_time=payload.open_time,
        close_time=payload.close_time,
        mode=payload.mode,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/attendance/sessions/{section_id}", response_model=list[AttendanceSessionRead])
def list_attendance_sessions(
    section_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor", "student")),
):
    return (
        db.query(AttendanceSession)
        .filter(AttendanceSession.section_id == section_id)
        .order_by(AttendanceSession.open_time.desc())
        .all()
    )


@router.post("/attendance/mark", response_model=AttendanceRecordRead)
def mark_attendance(
    payload: AttendanceMarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.get(AttendanceSession, payload.attendance_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Attendance session not found")

    now = datetime.utcnow()
    if now < session.open_time or now > session.close_time:
        raise HTTPException(status_code=400, detail="Attendance window not open")

    target_user_id = payload.user_id or current_user.id

    existing = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.attendance_session_id == payload.attendance_session_id,
            AttendanceRecord.user_id == target_user_id,
        )
        .first()
    )
    if existing:
        return existing

    record = AttendanceRecord(
        attendance_session_id=payload.attendance_session_id,
        user_id=target_user_id,
        status=payload.status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/attendance/records/{attendance_session_id}", response_model=list[AttendanceRecordRead])
def list_attendance_records(
    attendance_session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.attendance_session_id == attendance_session_id)
        .all()
    )
