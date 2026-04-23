from pydantic import BaseModel


class SEBPolicyCreate(BaseModel):
    assessment_id: int
    config_name: str
    quit_url: str | None = None
    require_config_key: bool = True
    require_browser_exam_key: bool = False


class SEBValidationResult(BaseModel):
    ok: bool
    message: str


class ExamSessionStartResponse(BaseModel):
    attempt_id: int
    assessment_id: int
    expires_at: str | None = None
    status: str
    exam_session_token: str
    resume_token: str | None = None


class ExamHeartbeatRequest(BaseModel):
    exam_session_token: str
    nonce: str | None = None


class ExamSubmitRequest(BaseModel):
    exam_session_token: str
    submitted_payload: dict | None = None


class IncidentDashboardRow(BaseModel):
    incident_id: int
    attempt_id: int
    assessment_id: int | None = None
    user_id: int | None = None
    incident_type: str
    details_json: str | None = None
    created_at: str | None = None
