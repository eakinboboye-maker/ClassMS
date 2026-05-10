from datetime import datetime
from pydantic import BaseModel


class LessonLaunchConfigCreate(BaseModel):
    lesson_slug: str
    course_code: str
    title: str
    assessment_id: int
    attendance_session_id: int | None = None
    question_keys: dict[str, int] = {}
    notebook_path: str | None = None
    attendance_open_at: datetime | None = None
    attendance_close_at: datetime | None = None
    show_on_portal: bool = True
    allow_portal_mock_exam: bool = False
    is_active: bool = True


class LessonLaunchConfigUpdate(BaseModel):
    title: str | None = None
    assessment_id: int | None = None
    attendance_session_id: int | None = None
    question_keys: dict[str, int] | None = None
    notebook_path: str | None = None
    attendance_open_at: datetime | None = None
    attendance_close_at: datetime | None = None
    show_on_portal: bool | None = None
    allow_portal_mock_exam: bool | None = None
    is_active: bool | None = None


class AttendanceWindowRead(BaseModel):
    lesson_slug: str
    attendance_open_at: datetime | None = None
    attendance_close_at: datetime | None = None
    is_open_now: bool
    already_marked: bool


class PortalLessonRead(BaseModel):
    lesson_slug: str
    title: str
    course_code: str
    notebook_path: str | None = None
    attendance: AttendanceWindowRead | None = None


class PortalPerformanceItem(BaseModel):
    attempt_id: int
    assessment_id: int
    assessment_title: str
    assessment_type: str
    submitted_at: str | None = None
    total_awarded: float
    total_max: float
    percent: float


class PortalHomeResponse(BaseModel):
    lessons: list[PortalLessonRead]
    mock_exams: list[dict]
    performance: dict
