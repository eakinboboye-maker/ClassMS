import json
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.security_exam import ApprovedConfigKey, IncidentLog


def extract_seb_headers(request: Request) -> dict:
    return {
        "seb_config_key": request.headers.get("X-SafeExamBrowser-ConfigKeyHash"),
        "seb_browser_exam_key": request.headers.get("X-SafeExamBrowser-BrowserExamKey"),
        "user_agent": request.headers.get("user-agent", ""),
    }


def validate_seb_for_assessment(db: Session, assessment_id: int, request: Request) -> bool:
    if not settings.SEB_REQUIRED_FOR_FORMAL_EXAMS:
        return True

    headers = extract_seb_headers(request)
    config_key = headers["seb_config_key"]

    if not config_key:
        raise HTTPException(status_code=403, detail="SEB Config Key missing")

    approved = db.query(ApprovedConfigKey).filter(
        ApprovedConfigKey.assessment_id == assessment_id,
        ApprovedConfigKey.key_hash == config_key,
    ).first()

    if not approved:
        raise HTTPException(status_code=403, detail="Invalid SEB Config Key")

    return True


def log_seb_incident(db: Session, attempt_id: int, incident_type: str, details: dict | None = None):
    db.add(
        IncidentLog(
            attempt_id=attempt_id,
            incident_type=incident_type,
            details_json=json.dumps(details or {}),
        )
    )
    db.commit()
