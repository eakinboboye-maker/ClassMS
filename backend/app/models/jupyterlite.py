from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LessonLaunchConfig(Base):
    __tablename__ = "lesson_launch_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_slug: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    course_code: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(255))
    assessment_id: Mapped[int] = mapped_column(Integer, index=True)
    attendance_session_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    question_keys_json: Mapped[str] = mapped_column(Text, default="{}")
    notebook_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attendance_open_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    attendance_close_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    show_on_portal: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_portal_mock_exam: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
