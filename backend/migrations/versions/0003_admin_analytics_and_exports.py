"""add admin/analytics/export support

Revision ID: 0003_admin_analytics_and_exports
Revises: 0002_grade_publications_and_exam_tokens
Create Date: 2026-04-20 00:15:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_admin_analytics_and_exports"
down_revision = "0002_grade_publications_and_exam_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No new core tables were required for analytics/export endpoints because
    # they derive from existing tables. This migration is kept to mark the
    # schema/application checkpoint and can be extended later if new persisted
    # analytics tables are introduced.
    pass


def downgrade() -> None:
    pass
