"""add lesson launch configs

Revision ID: 0004_lesson_launch_configs
Revises: 0003_admin_analytics_and_exports
Create Date: 2026-04-28 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_lesson_launch_configs"
down_revision = "0003_admin_analytics_and_exports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lesson_launch_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_slug", sa.String(length=150), nullable=False),
        sa.Column("course_code", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("attendance_session_id", sa.Integer(), nullable=False),
        sa.Column("question_keys_json", sa.Text(), nullable=False),
        sa.Column("notebook_path", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_lesson_launch_configs_lesson_slug", "lesson_launch_configs", ["lesson_slug"], unique=True)
    op.create_index("ix_lesson_launch_configs_course_code", "lesson_launch_configs", ["course_code"], unique=False)
    op.create_index("ix_lesson_launch_configs_assessment_id", "lesson_launch_configs", ["assessment_id"], unique=False)
    op.create_index("ix_lesson_launch_configs_attendance_session_id", "lesson_launch_configs", ["attendance_session_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lesson_launch_configs_attendance_session_id", table_name="lesson_launch_configs")
    op.drop_index("ix_lesson_launch_configs_assessment_id", table_name="lesson_launch_configs")
    op.drop_index("ix_lesson_launch_configs_course_code", table_name="lesson_launch_configs")
    op.drop_index("ix_lesson_launch_configs_lesson_slug", table_name="lesson_launch_configs")
    op.drop_table("lesson_launch_configs")
