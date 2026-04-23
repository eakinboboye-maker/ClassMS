import csv
import io
import json
from sqlalchemy.orm import Session

from app.models.security_exam import IncidentLog
from app.models.assessment import Attempt


def export_incidents_as_json(db: Session, assessment_id: int | None = None) -> list[dict]:
    query = db.query(IncidentLog, Attempt).join(Attempt, Attempt.id == IncidentLog.attempt_id)
    if assessment_id is not None:
        query = query.filter(Attempt.assessment_id == assessment_id)

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


def export_incidents_as_csv(db: Session, assessment_id: int | None = None) -> str:
    rows = export_incidents_as_json(db, assessment_id=assessment_id)
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "incident_id",
            "attempt_id",
            "assessment_id",
            "user_id",
            "incident_type",
            "details_json",
            "created_at",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
