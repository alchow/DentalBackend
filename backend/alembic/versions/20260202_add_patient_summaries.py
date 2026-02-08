"""Add patient_summaries table

Revision ID: 20260202_add_patient_summaries
Revises: 20260201_add_ssn_fields
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '20260202_add_patient_summaries'
down_revision = '8b3c4d5e6f7a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'patient_summaries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('patient_id', UUID(as_uuid=True), sa.ForeignKey('patients.id'), nullable=False),
        
        # Content (encrypted)
        sa.Column('content_encrypted', sa.Text, nullable=False),
        
        # Metadata
        sa.Column('source', sa.String(20), nullable=False),  # 'AI' or 'MANUAL'
        sa.Column('model_provider', sa.String(20), nullable=True),  # openai, gemini, anthropic
        sa.Column('model_name', sa.String(50), nullable=True),
        sa.Column('prompt_version', sa.String(20), nullable=True),  # v1, v2, etc.
        sa.Column('confidence_score', sa.Float, nullable=True),
        
        # Audit
        sa.Column('triggered_by_note_id', UUID(as_uuid=True), sa.ForeignKey('notes.id'), nullable=True),
        sa.Column('edited_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('notes_context', JSONB, nullable=True),  # IDs of notes used
        
        # Timestamps & Tenant
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('office_id', UUID(as_uuid=True), sa.ForeignKey('offices.id'), nullable=True),
    )
    
    # Indexes
    op.create_index('idx_summaries_patient_created', 'patient_summaries', ['patient_id', sa.text('created_at DESC')])
    op.create_index('idx_summaries_office', 'patient_summaries', ['office_id'])


def downgrade() -> None:
    op.drop_index('idx_summaries_office')
    op.drop_index('idx_summaries_patient_created')
    op.drop_table('patient_summaries')
