"""add_deleted_to_visitstatus_enum

Revision ID: add_deleted_enum
Revises: 20260127_1824_add_multi_tenancy_tables
Create Date: 2026-01-29
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_deleted_enum'
down_revision = 'b45198b26479'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add DELETED value to the existing visitstatus enum type
    # PostgreSQL requires using ALTER TYPE to add new enum values
    op.execute("ALTER TYPE visitstatus ADD VALUE IF NOT EXISTS 'DELETED'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly
    # To downgrade, you would need to recreate the type without DELETED
    # This is a complex operation that requires recreating the column
    # For safety, we leave this as a no-op with a warning
    pass
