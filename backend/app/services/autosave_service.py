import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.response import Response, AutosaveEvent
from app.models.assessment import Attempt, Submission


def save_response(db: Session, attempt_id: int, question_id: int, response_payload: dict, is_final: bool = False) -> Response:
    existing = db.query(Response).filter(
        Response.attempt_id == attempt_id,
        Response.question_id == question_id,
    ).first()

    if existing:
        existing.response_json = json.dumps(response_payload)
        existing.is_final = is_final
        existing.updated_at = datetime.utcnow()
        obj = existing
    else:
        obj = Response(
            attempt_id=attempt_id,
            question_id=question_id,
            response_json=json.dumps(response_payload),
            is_final=is_final,
        )
        db.add(obj)

    db.flush()

    db.add(
        AutosaveEvent(
            attempt_id=attempt_id,
            question_id=question_id,
            payload_json=json.dumps(response_payload),
            event_type="final_save" if is_final else "autosave",
        )
    )
    db.commit()
    db.refresh(obj)
    return obj


def get_attempt_responses(db: Session, attempt_id: int) -> list[Response]:
    return db.query(Response).filter(Response.attempt_id == attempt_id).all()


def finalize_attempt(db: Session, attempt: Attempt, submitted_payload: dict | None = None) -> Submission:
    attempt.status = "submitted"
    attempt.submitted_at = datetime.utcnow()

    submission = Submission(
        attempt_id=attempt.id,
        submitted_payload_json=json.dumps(submitted_payload or {}),
        finalized_at=datetime.utcnow(),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
