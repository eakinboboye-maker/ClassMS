from pydantic import BaseModel


class AttemptMonitorRow(BaseModel):
    attempt_id: int
    user_id: int
    status: str
    started_at: str | None = None
    expires_at: str | None = None
    submitted_at: str | None = None
    is_auto_submitted: bool
    seb_validated: bool
    incident_flag: bool
    resume_token: str | None = None


class LiveMonitorRow(BaseModel):
    attempt_id: int
    user_id: int
    assessment_id: int
    started_at: str | None = None
    last_seen_at: str | None = None
    config_key_valid: bool
    browser_exam_key_valid: bool
    session_token: str | None = None
    is_active: bool


class AdminIncidentDashboardResponse(BaseModel):
    rows: list[dict]
