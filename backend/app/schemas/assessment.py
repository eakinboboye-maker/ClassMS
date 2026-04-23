from datetime import datetime
from pydantic import BaseModel, field_validator


class AssessmentCreate(BaseModel):
    title: str
    type: str
    section_id: int
    duration_minutes: int = 60
    shuffle_questions: bool = False
    requires_seb: bool = False
    allow_resume: bool = True
    instructions_md: str | None = None
    question_ids: list[int]
    open_time: datetime
    close_time: datetime
    candidate_user_ids: list[int] = []

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str):
        if value not in {"mock", "formal"}:
            raise ValueError("type must be 'mock' or 'formal'")
        return value

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, value: int):
        if value <= 0:
            raise ValueError("duration_minutes must be positive")
        return value


class AssessmentRead(BaseModel):
    id: int
    title: str
    type: str
    section_id: int
    duration_minutes: int
    status: str
    requires_seb: bool

    class Config:
        from_attributes = True


class StartAssessmentResponse(BaseModel):
    attempt_id: int
    assessment_id: int
    expires_at: datetime | None = None
    status: str


class AssessmentBlueprintRule(BaseModel):
    question_type: str | None = None
    difficulty: str | None = None
    topic: str | None = None
    count: int


class AssessmentBlueprintCreate(BaseModel):
    title: str
    type: str
    section_id: int
    duration_minutes: int = 60
    shuffle_questions: bool = False
    requires_seb: bool = False
    allow_resume: bool = True
    instructions_md: str | None = None
    rules: list[AssessmentBlueprintRule]
    open_time: datetime
    close_time: datetime
    candidate_user_ids: list[int] = []
