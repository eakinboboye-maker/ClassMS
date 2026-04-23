import secrets
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.assessment import Attempt
from app.models.security_exam import ExamSession, IncidentLog


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def start_exam_session(db: Session, attempt: Attempt) -> ExamSession:
    session = ExamSession(
        attempt_id=attempt.id,
        user_id=attempt.user_id,
        assessment_id=attempt.assessment_id,
        config_key_valid=True,
        browser_exam_key_valid=False,
        session_token=generate_token(),
        session_nonce=generate_token(),
        is_active=True,
    )
    attempt.resume_token = generate_token()
    db.add(session)
    db.flush()
    return session


def get_active_exam_session(db: Session, attempt_id: int) -> ExamSession | None:
    return (
        db.query(ExamSession)
        .filter(ExamSession.attempt_id == attempt_id, ExamSession.is_active.is_(True))
        .order_by(ExamSession.id.desc())
        .first()
    )


def validate_exam_session_token(
    db: Session,
    attempt_id: int,
    user_id: int,
    exam_session_token: str,
) -> ExamSession:
    session = (
        db.query(ExamSession)
        .filter(
            ExamSession.attempt_id == attempt_id,
            ExamSession.user_id == user_id,
            ExamSession.session_token == exam_session_token,
            ExamSession.is_active.is_(True),
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=403, detail="Invalid or inactive exam session token")
    return session


def rotate_exam_session_nonce(db: Session, session: ExamSession) -> str:
    session.session_nonce = generate_token()
    session.last_seen_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session.session_nonce


def invalidate_other_exam_sessions(db: Session, attempt_id: int, keep_session_id: int):
    sessions = (
        db.query(ExamSession)
        .filter(ExamSession.attempt_id == attempt_id, ExamSession.id != keep_session_id)
        .all()
    )
    for s in sessions:
        s.is_active = False
    db.commit()


def log_replay_incident(db: Session, attempt_id: int, details: dict | None = None):
    db.add(
        IncidentLog(
            attempt_id=attempt_id,
            incident_type="replay_or_invalid_session",
            details_json=str(details or {}),
        )
    )
    db.commit()
