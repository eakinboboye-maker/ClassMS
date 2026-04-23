from pydantic import BaseModel


class SectionAnalyticsRow(BaseModel):
    assessment_id: int
    assessment_title: str
    attempts_count: int
    submitted_count: int
    avg_awarded: float
    avg_max: float


class CourseAnalyticsRow(BaseModel):
    section_id: int
    course_id: int
    assessments_count: int
    submitted_count: int
    avg_awarded: float
    avg_max: float
