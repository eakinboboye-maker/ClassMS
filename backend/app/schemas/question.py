from pydantic import BaseModel, field_validator, model_validator


class QuestionOptionCreate(BaseModel):
    option_key: str
    text: str
    is_correct: bool = False


class QuestionGapCreate(BaseModel):
    gap_key: str
    marks: int = 1
    position: int = 0
    accepted_answers: list[str]


class RubricCriterionCreate(BaseModel):
    criterion: str
    points: int


class QuestionCreate(BaseModel):
    type: str
    prompt_md: str
    marks: int = 1
    difficulty: str | None = None
    topics: list[str] = []
    grading_mode: str | None = None
    options: list[QuestionOptionCreate] = []
    gaps: list[QuestionGapCreate] = []
    answer_key: dict | None = None
    rubric: list[RubricCriterionCreate] = []
    explanation_md: str | None = None
    show_explanation_after_submit: bool = False

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str):
        allowed = {"mcq_single", "mcq_multi", "fill_gap", "short_answer", "essay"}
        if value not in allowed:
            raise ValueError(f"Unsupported question type: {value}")
        return value

    @model_validator(mode="after")
    def validate_by_type(self):
        if self.type == "mcq_single":
            if len(self.options) < 2:
                raise ValueError("mcq_single requires at least 2 options")
            correct_count = sum(1 for o in self.options if o.is_correct)
            if correct_count != 1:
                raise ValueError("mcq_single must have exactly one correct option")

        if self.type == "mcq_multi":
            if len(self.options) < 2:
                raise ValueError("mcq_multi requires at least 2 options")
            correct_count = sum(1 for o in self.options if o.is_correct)
            if correct_count < 1:
                raise ValueError("mcq_multi must have at least one correct option")

        if self.type == "fill_gap":
            if not self.gaps:
                raise ValueError("fill_gap requires at least one gap")
            if any(not g.accepted_answers for g in self.gaps):
                raise ValueError("each gap must have accepted answers")

        if self.type in {"short_answer", "essay"}:
            if not self.answer_key and not self.rubric:
                raise ValueError("essay/short_answer should have answer_key or rubric")
        return self


class QuestionRead(BaseModel):
    id: int
    type: str
    prompt_md: str
    marks: int
    difficulty: str | None = None
    topics_json: str | None = None
    grading_mode: str | None = None
    explanation_md: str | None = None
    show_explanation_after_submit: bool = False

    class Config:
        from_attributes = True


class QuestionBankImportRequest(BaseModel):
    questions: list[QuestionCreate]


class QuestionBankExportItem(BaseModel):
    id: int
    type: str
    prompt_md: str
    marks: int
    difficulty: str | None = None
    topics: list[str]
    grading_mode: str | None = None
    options: list[dict] = []
    gaps: list[dict] = []
    answer_key: dict | None = None


class QuestionBankExportResponse(BaseModel):
    questions: list[QuestionBankExportItem]
