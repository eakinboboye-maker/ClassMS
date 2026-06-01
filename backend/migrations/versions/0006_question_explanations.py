"""add question explanation fields

Revision ID: 0006_question_explanations
Revises: 0005_portal_cfg
Create Date: 2026-05-31
"""
from alembic import op
import sqlalchemy as sa


revision = "0006_question_explanations"
down_revision = "0005_portal_cfg"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("explanation_md", sa.Text(), nullable=True))
    op.add_column(
        "questions",
        sa.Column(
            "show_explanation_after_submit",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("questions", "show_explanation_after_submit")
    op.drop_column("questions", "explanation_md")
