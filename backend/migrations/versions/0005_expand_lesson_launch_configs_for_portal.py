"""expand lesson launch configs for portal

Revision ID: 0005_expand_lesson_launch_configs_for_portal
Revises: 0004_lesson_launch_configs
Create Date: 2026-05-10 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_expand_lesson_launch_configs_for_portal"
down_revision = "0004_lesson_launch_configs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("lesson_launch_configs", sa.Column("attendance_open_at", sa.DateTime(), nullable=True))
    op.add_column("lesson_launch_configs", sa.Column("attendance_close_at", sa.DateTime(), nullable=True))
    op.add_column("lesson_launch_configs", sa.Column("show_on_portal", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("lesson_launch_configs", sa.Column("allow_portal_mock_exam", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("lesson_launch_configs", "attendance_session_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column("lesson_launch_configs", "attendance_session_id", existing_type=sa.Integer(), nullable=False)
    op.drop_column("lesson_launch_configs", "allow_portal_mock_exam")
    op.drop_column("lesson_launch_configs", "show_on_portal")
    op.drop_column("lesson_launch_configs", "attendance_close_at")
    op.drop_column("lesson_launch_configs", "attendance_open_at")
