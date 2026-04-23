from datetime import datetime
from pydantic import BaseModel


class CourseCreate(BaseModel):
    code: str
    title: str
    description: str | None = None


class CourseRead(BaseModel):
    id: int
    code: str
    title: str
    description: str | None = None

    class Config:
        from_attributes = True


class SectionCreate(BaseModel):
    course_id: int
    name: str
    term: str
    instructor_id: int | None = None


class SectionRead(BaseModel):
    id: int
    course_id: int
    name: str
    term: str
    instructor_id: int | None = None

    class Config:
        from_attributes = True


class EnrollmentCreate(BaseModel):
    user_id: int
    section_id: int


class AttendanceSessionCreate(BaseModel):
    section_id: int
    title: str
    open_time: datetime
    close_time: datetime
    mode: str = "checkpoint"


class AttendanceSessionRead(BaseModel):
    id: int
    section_id: int
    title: str
    open_time: datetime
    close_time: datetime
    mode: str

    class Config:
        from_attributes = True


class AttendanceMarkRequest(BaseModel):
    attendance_session_id: int
    user_id: int | None = None
    status: str = "present"


class AttendanceRecordRead(BaseModel):
    id: int
    attendance_session_id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True
