"""add question explanation fields

Revision ID: 0006_question_explanations
Revises: 0005_portal_cfg
Create Date: 2026-05-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("questions")}

    if "explanation_md" not in columns:
        op.add_column(
            "questions",
            sa.Column("explanation_md", sa.Text(), nullable=True),
        )

    if "show_explanation_after_submit" not in columns:
        op.add_column(
            "questions",
            sa.Column(
                "show_explanation_after_submit",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )

    # Optional: remove server default after existing rows are safe
    # with op.batch_alter_table("questions") as batch_op:
    #     batch_op.alter_column("show_explanation_after_submit", server_default=None)
    
    
def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("questions")}

    if "show_explanation_after_submit" in columns:
        op.drop_column("questions", "show_explanation_after_submit")

    if "explanation_md" in columns:
        op.drop_column("questions", "explanation_md")
