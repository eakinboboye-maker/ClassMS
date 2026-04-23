"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-19 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("matric_no", sa.String(length=100), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_matric_no", "users", ["matric_no"], unique=True)

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_courses_code", "courses", ["code"], unique=True)

    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("term", sa.String(length=100), nullable=False),
        sa.Column("instructor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("section_id", sa.Integer(), sa.ForeignKey("sections.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
    )

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("prompt_md", sa.Text(), nullable=False),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("topics_json", sa.Text(), nullable=True),
        sa.Column("answer_key_json", sa.Text(), nullable=True),
        sa.Column("grading_mode", sa.String(length=50), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
    )

    op.create_table(
        "question_options",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("option_key", sa.String(length=10), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "question_gaps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("gap_key", sa.String(length=50), nullable=False),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
    )

    op.create_table(
        "accepted_answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("gap_id", sa.Integer(), sa.ForeignKey("question_gaps.id"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
    )

    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("section_id", sa.Integer(), sa.ForeignKey("sections.id"), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("shuffle_questions", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("requires_seb", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("allow_resume", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("instructions_md", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "assessment_windows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("open_time", sa.DateTime(), nullable=False),
        sa.Column("close_time", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "assessment_candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "assessment_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("points_override", sa.Integer(), nullable=True),
        sa.Column("frozen_question_version", sa.Integer(), nullable=False),
    )

    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("is_auto_submitted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("seb_validated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("incident_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("submitted_payload_json", sa.Text(), nullable=True),
        sa.Column("finalized_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "responses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("response_json", sa.Text(), nullable=False),
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "autosave_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("awarded_marks", sa.Float(), nullable=False),
        sa.Column("max_marks", sa.Float(), nullable=False),
        sa.Column("graded_by", sa.String(length=100), nullable=True),
        sa.Column("grading_method", sa.String(length=50), nullable=False),
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "ai_grading_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("response_id", sa.Integer(), sa.ForeignKey("responses.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("queued_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "ai_grading_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("ai_grading_jobs.id"), nullable=False),
        sa.Column("proposed_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("criteria_json", sa.Text(), nullable=False),
        sa.Column("flags_json", sa.Text(), nullable=False),
        sa.Column("rationale_json", sa.Text(), nullable=False),
    )

    op.create_table(
        "grading_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("response_id", sa.Integer(), sa.ForeignKey("responses.id"), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("final_score", sa.Float(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
    )

    op.create_table(
        "seb_policies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("config_name", sa.String(length=255), nullable=False),
        sa.Column("quit_url", sa.String(length=500), nullable=True),
        sa.Column("require_config_key", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("require_browser_exam_key", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "seb_approved_config_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("key_hash", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "seb_approved_browser_exam_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("key_hash", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "exam_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("config_key_valid", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("browser_exam_key_valid", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "incident_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("incident_type", sa.String(length=100), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "attendance_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("section_id", sa.Integer(), sa.ForeignKey("sections.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("open_time", sa.DateTime(), nullable=False),
        sa.Column("close_time", sa.DateTime(), nullable=False),
        sa.Column("mode", sa.String(length=50), nullable=False),
    )

    op.create_table(
        "attendance_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attendance_session_id", sa.Integer(), sa.ForeignKey("attendance_sessions.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("marked_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("attendance_records")
    op.drop_table("attendance_sessions")
    op.drop_table("incident_logs")
    op.drop_table("exam_sessions")
    op.drop_table("seb_approved_browser_exam_keys")
    op.drop_table("seb_approved_config_keys")
    op.drop_table("seb_policies")
    op.drop_table("grading_reviews")
    op.drop_table("ai_grading_results")
    op.drop_table("ai_grading_jobs")
    op.drop_table("scores")
    op.drop_table("autosave_events")
    op.drop_table("responses")
    op.drop_table("submissions")
    op.drop_table("attempts")
    op.drop_table("assessment_items")
    op.drop_table("assessment_candidates")
    op.drop_table("assessment_windows")
    op.drop_table("assessments")
    op.drop_table("accepted_answers")
    op.drop_table("question_gaps")
    op.drop_table("question_options")
    op.drop_table("questions")
    op.drop_table("enrollments")
    op.drop_table("sections")
    op.drop_index("ix_courses_code", table_name="courses")
    op.drop_table("courses")
    op.drop_index("ix_users_matric_no", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
