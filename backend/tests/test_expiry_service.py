from datetime import datetime, timedelta

from app.models.assessment import Attempt
from app.services.expiry_service import auto_submit_expired_attempts


def test_auto_submit_expired_attempts(db_session):
    attempt = Attempt(
        assessment_id=1,
        user_id=1,
        status="in_progress",
        started_at=datetime.utcnow() - timedelta(hours=2),
        expires_at=datetime.utcnow() - timedelta(minutes=5),
    )
    db_session.add(attempt)
    db_session.commit()

    ids = auto_submit_expired_attempts(db_session)
    assert attempt.id in ids
