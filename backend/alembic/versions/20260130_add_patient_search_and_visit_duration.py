"""add_patient_search_and_visit_duration

Revision ID: add_search_duration
Revises: add_archive_feature
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_search_duration'
down_revision = 'add_archive_feature'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add first_name_hash for patient search by first name
    op.add_column('patients', sa.Column('first_name_hash', sa.String(64), nullable=True))
    op.create_index('ix_patients_first_name_hash', 'patients', ['first_name_hash'])
    
    # 2. Add phone_hash for patient search by phone
    op.add_column('patients', sa.Column('phone_hash', sa.String(64), nullable=True))
    op.create_index('ix_patients_phone_hash', 'patients', ['phone_hash'])
    
    # 3. Add duration_minutes to visits (default 30 min standard appointment)
    op.add_column('visits', sa.Column('duration_minutes', sa.Integer(), nullable=True, server_default='30'))


def downgrade() -> None:
    # Remove visit duration
    op.drop_column('visits', 'duration_minutes')
    
    # Remove patient search indexes
    op.drop_index('ix_patients_phone_hash', table_name='patients')
    op.drop_column('patients', 'phone_hash')
    op.drop_index('ix_patients_first_name_hash', table_name='patients')
    op.drop_column('patients', 'first_name_hash')
