from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    awarded_marks: Mapped[float] = mapped_column(Float, default=0)
    max_marks: Mapped[float] = mapped_column(Float, default=0)
    graded_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    grading_method: Mapped[str] = mapped_column(String(50), default="objective")
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)


class AIGradingJob(Base):
    __tablename__ = "ai_grading_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    response_id: Mapped[int] = mapped_column(ForeignKey("responses.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    queued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AIGradingResult(Base):
    __tablename__ = "ai_grading_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("ai_grading_jobs.id"), index=True)
    proposed_score: Mapped[float] = mapped_column(Float, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    criteria_json: Mapped[str] = mapped_column(Text)
    flags_json: Mapped[str] = mapped_column(Text)
    rationale_json: Mapped[str] = mapped_column(Text)


class GradingReview(Base):
    __tablename__ = "grading_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    response_id: Mapped[int] = mapped_column(ForeignKey("responses.id"), index=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class GradePublication(Base):
    __tablename__ = "grade_publications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    published_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
