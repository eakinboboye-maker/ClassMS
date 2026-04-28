from pydantic import BaseModel


class LessonLaunchConfigCreate(BaseModel):
    lesson_slug: str
    course_code: str
    title: str
    assessment_id: int
    attendance_session_id: int
    question_keys: dict[str, int] = {}
    notebook_path: str | None = None
    is_active: bool = True


class LessonLaunchConfigUpdate(BaseModel):
    title: str | None = None
    assessment_id: int | None = None
    attendance_session_id: int | None = None
    question_keys: dict[str, int] | None = None
    notebook_path: str | None = None
    is_active: bool | None = None
