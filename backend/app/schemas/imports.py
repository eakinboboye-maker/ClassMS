from pydantic import BaseModel


class ParsedQuestionOption(BaseModel):
    option_key: str
    text: str
    is_correct: bool = False
    explanation_md: str | None = None


class ParsedQuestionRow(BaseModel):
    type: str
    prompt_md: str
    marks: int = 1
    topics: list[str] = []
    labels: list[str] = []
    options: list[ParsedQuestionOption] = []
    answer_key: dict | None = None
    explanation_md: str | None = None
    show_explanation_after_submit: bool = False
    grading_mode: str | None = None


class ParseQuestionTextRequest(BaseModel):
    text: str


class ParseQuestionTextResponse(BaseModel):
    count: int
    items: list[ParsedQuestionRow]
    warnings: list[str] = []


class PublishParsedQuestionsRequest(BaseModel):
    items: list[ParsedQuestionRow]


class PublishParsedQuestionsResponse(BaseModel):
    created_count: int
    created_ids: list[int]


class ParsedEnrollmentRow(BaseModel):
    reg_no: str
    course_code: str
    section: str
    session: str


class ParseEnrollmentRowsRequest(BaseModel):
    rows: list[dict]


class ParseEnrollmentRowsResponse(BaseModel):
    parsed_count: int
    rows: list[ParsedEnrollmentRow]
    errors: list[dict] = []


class BulkEnrollmentRequest(BaseModel):
    rows: list[ParsedEnrollmentRow]


class BulkEnrollmentResponse(BaseModel):
    enrolled_count: int
    skipped_count: int
    details: list[dict]
