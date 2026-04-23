"""add grade publications and exam session token support

Revision ID: 0002_grade_pub_examtok
Revises: 0001_initial
...
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_grade_pub_examtok"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "grade_publications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("assessments.id"), nullable=False),
        sa.Column("published_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
    )

    op.add_column("exam_sessions", sa.Column("session_token", sa.String(length=255), nullable=True))
    op.add_column("exam_sessions", sa.Column("session_nonce", sa.String(length=255), nullable=True))
    op.add_column("exam_sessions", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_exam_sessions_session_token", "exam_sessions", ["session_token"], unique=False)

    op.add_column("attempts", sa.Column("resume_token", sa.String(length=255), nullable=True))
    op.create_index("ix_attempts_resume_token", "attempts", ["resume_token"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_attempts_resume_token", table_name="attempts")
    op.drop_column("attempts", "resume_token")

    op.drop_index("ix_exam_sessions_session_token", table_name="exam_sessions")
    op.drop_column("exam_sessions", "is_active")
    op.drop_column("exam_sessions", "session_nonce")
    op.drop_column("exam_sessions", "session_token")

    op.drop_table("grade_publications")
