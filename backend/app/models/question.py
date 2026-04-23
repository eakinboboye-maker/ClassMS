from sqlalchemy import ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(50), index=True)  # mcq_single, mcq_multi, fill_gap, short_answer, essay
    prompt_md: Mapped[str] = mapped_column(Text)
    marks: Mapped[int] = mapped_column(Integer, default=1)
    difficulty: Mapped[str | None] = mapped_column(String(50), nullable=True)
    topics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_key_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    grading_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    option_key: Mapped[str] = mapped_column(String(10))
    text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)


class QuestionGap(Base):
    __tablename__ = "question_gaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    gap_key: Mapped[str] = mapped_column(String(50))
    marks: Mapped[int] = mapped_column(Integer, default=1)
    position: Mapped[int] = mapped_column(Integer, default=0)


class AcceptedAnswer(Base):
    __tablename__ = "accepted_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gap_id: Mapped[int] = mapped_column(ForeignKey("question_gaps.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    normalized_text: Mapped[str] = mapped_column(Text)
