"""Add SSN fields to patients table

Revision ID: 20260201_add_ssn_fields
Revises: 20260201_add_backfill_flag
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260201_add_ssn_fields'
down_revision = '20260201_add_backfill_flag'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add SSN columns to patients table
    op.add_column('patients', sa.Column('ssn_encrypted', sa.String(), nullable=True))
    op.add_column('patients', sa.Column('ssn_hash', sa.String(64), nullable=True))
    op.add_column('patients', sa.Column('last_4_ssn_hash', sa.String(64), nullable=True))
    
    # Create indexes for searchability
    op.create_index('ix_patients_ssn_hash', 'patients', ['ssn_hash'])
    op.create_index('ix_patients_last_4_ssn_hash', 'patients', ['last_4_ssn_hash'])


def downgrade() -> None:
    op.drop_index('ix_patients_last_4_ssn_hash', table_name='patients')
    op.drop_index('ix_patients_ssn_hash', table_name='patients')
    op.drop_column('patients', 'last_4_ssn_hash')
    op.drop_column('patients', 'ssn_hash')
    op.drop_column('patients', 'ssn_encrypted')
