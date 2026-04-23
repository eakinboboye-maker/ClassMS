from sqlalchemy.orm import Session

from app.models.security_exam import IncidentLog
from app.models.assessment import Attempt


def get_incident_dashboard(
    db: Session,
    assessment_id: int | None = None,
    user_id: int | None = None,
    incident_type: str | None = None,
) -> list[dict]:
    query = db.query(IncidentLog, Attempt).join(Attempt, Attempt.id == IncidentLog.attempt_id)

    if assessment_id is not None:
        query = query.filter(Attempt.assessment_id == assessment_id)
    if user_id is not None:
        query = query.filter(Attempt.user_id == user_id)
    if incident_type is not None:
        query = query.filter(IncidentLog.incident_type == incident_type)

    query = query.order_by(IncidentLog.created_at.desc())

    rows = []
    for incident, attempt in query.all():
        rows.append(
            {
                "incident_id": incident.id,
                "attempt_id": incident.attempt_id,
                "assessment_id": attempt.assessment_id,
                "user_id": attempt.user_id,
                "incident_type": incident.incident_type,
                "details_json": incident.details_json,
                "created_at": incident.created_at.isoformat() if incident.created_at else None,
            }
        )
    return rows
