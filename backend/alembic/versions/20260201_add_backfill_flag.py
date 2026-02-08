"""Add is_backfilled column to notes, patients, visits, bills

Revision ID: 20260201_add_backfill_flag
Revises: 
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260201_add_backfill_flag'
down_revision = '20260131_add_notes_indexes'  # Correct parent in migration chain
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_backfilled column with default False to all four tables
    op.add_column('notes', sa.Column('is_backfilled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('patients', sa.Column('is_backfilled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('visits', sa.Column('is_backfilled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('bills', sa.Column('is_backfilled', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('bills', 'is_backfilled')
    op.drop_column('visits', 'is_backfilled')
    op.drop_column('patients', 'is_backfilled')
    op.drop_column('notes', 'is_backfilled')
