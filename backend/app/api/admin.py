from fastapi import APIRouter, Depends, Body, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User
from app.models.assessment import Assessment, Attempt
from app.models.security_exam import SEBPolicy, ApprovedConfigKey, IncidentLog, ExamSession
from app.schemas.security_exam import SEBPolicyCreate
from app.services.incident_dashboard_service import get_incident_dashboard
from app.services.audit_export_service import export_incidents_as_json, export_incidents_as_csv

router = APIRouter()


@router.post("/seb-policy")
def create_seb_policy(
    payload: SEBPolicyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    policy = SEBPolicy(**payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.post("/seb-config-key/{assessment_id}")
def register_seb_config_key(
    assessment_id: int,
    config_key_hash: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    item = ApprovedConfigKey(
        assessment_id=assessment_id,
        key_hash=config_key_hash,
    )
    db.add(item)
    db.commit()
    return {"status": "ok"}


@router.get("/incidents")
def list_incidents(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return db.query(IncidentLog).all()


@router.get("/incidents/dashboard")
def incident_dashboard(
    assessment_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    incident_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return {
        "rows": get_incident_dashboard(
            db,
            assessment_id=assessment_id,
            user_id=user_id,
            incident_type=incident_type,
        )
    }


@router.get("/incidents/export.json")
def export_incidents_json(
    assessment_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return JSONResponse(content={"rows": export_incidents_as_json(db, assessment_id=assessment_id)})


@router.get("/incidents/export.csv", response_class=PlainTextResponse)
def export_incidents_csv(
    assessment_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return export_incidents_as_csv(db, assessment_id=assessment_id)


@router.get("/assessments/{assessment_id}/attempts")
def list_assessment_attempts(
    assessment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    assessment = db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    attempts = (
        db.query(Attempt)
        .filter(Attempt.assessment_id == assessment_id)
        .order_by(Attempt.started_at.desc())
        .all()
    )

    return [
        {
            "attempt_id": a.id,
            "user_id": a.user_id,
            "status": a.status,
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "expires_at": a.expires_at.isoformat() if a.expires_at else None,
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
            "is_auto_submitted": a.is_auto_submitted,
            "seb_validated": a.seb_validated,
            "incident_flag": a.incident_flag,
            "resume_token": a.resume_token,
        }
        for a in attempts
    ]


@router.get("/assessments/{assessment_id}/live-monitor")
def live_monitor_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    assessment = db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    sessions = (
        db.query(ExamSession)
        .filter(ExamSession.assessment_id == assessment_id)
        .order_by(ExamSession.last_seen_at.desc())
        .all()
    )

    return [
        {
            "attempt_id": s.attempt_id,
            "user_id": s.user_id,
            "assessment_id": s.assessment_id,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "last_seen_at": s.last_seen_at.isoformat() if s.last_seen_at else None,
            "config_key_valid": s.config_key_valid,
            "browser_exam_key_valid": s.browser_exam_key_valid,
            "session_token": s.session_token,
            "is_active": s.is_active,
        }
        for s in sessions
    ]


@router.post("/attempts/{attempt_id}/flag")
def flag_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    attempt = db.get(Attempt, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    attempt.incident_flag = True
    db.commit()
    return {"status": "flagged", "attempt_id": attempt_id}
