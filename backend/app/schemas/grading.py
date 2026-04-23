from pydantic import BaseModel


class AIGradingRequest(BaseModel):
    response_ids: list[int]


class ReviewDecisionRequest(BaseModel):
    approved: bool
    final_score: float
    reviewer_comment: str | None = None


class ScoreRead(BaseModel):
    question_id: int
    awarded_marks: float
    max_marks: float
    grading_method: str


class GradePublicationRequest(BaseModel):
    note: str | None = None


class GradebookRow(BaseModel):
    user_id: int
    attempt_id: int | None = None
    total_awarded: float
    total_max: float
    published: bool
    assessment_id: int | None = None
    section_id: int | None = None
    course_id: int | None = None


class GradebookFilterParams(BaseModel):
    course_id: int | None = None
    section_id: int | None = None
    assessment_id: int | None = None
    published_only: bool = False


class EssayReviewItem(BaseModel):
    review_id: int
    response_id: int
    question_id: int
    attempt_id: int
    user_id: int | None = None
    prompt_md: str
    student_answer: str
    proposed_score: float | None = None
    confidence: float | None = None
    criteria: list[dict] = []
    flags: list[str] = []
    rationale: dict | None = None
    max_marks: float
