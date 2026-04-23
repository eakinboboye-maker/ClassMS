from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SEBPolicy(Base):
    __tablename__ = "seb_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    config_name: Mapped[str] = mapped_column(String(255))
    quit_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    require_config_key: Mapped[bool] = mapped_column(Boolean, default=True)
    require_browser_exam_key: Mapped[bool] = mapped_column(Boolean, default=False)


class ApprovedConfigKey(Base):
    __tablename__ = "seb_approved_config_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    key_hash: Mapped[str] = mapped_column(String(255), index=True)


class ApprovedBrowserExamKey(Base):
    __tablename__ = "seb_approved_browser_exam_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    key_hash: Mapped[str] = mapped_column(String(255), index=True)


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    config_key_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    browser_exam_key_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    session_token: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    session_nonce: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class IncidentLog(Base):
    __tablename__ = "incident_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"), index=True)
    incident_type: Mapped[str] = mapped_column(String(100))
    details_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
