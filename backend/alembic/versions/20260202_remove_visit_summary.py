"""Remove unused summary column from visits table

Revision ID: 20260202_remove_visit_summary
Revises: 20260202_add_patient_summaries
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260202_remove_visit_summary'
down_revision = '20260202_add_patient_summaries'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the unused summary column from visits table
    # This column was never populated and is replaced by patient_summaries table
    op.drop_column('visits', 'summary')


def downgrade() -> None:
    # Restore the summary column if needed
    op.add_column('visits', sa.Column('summary', sa.dialects.postgresql.JSONB(), nullable=True))
