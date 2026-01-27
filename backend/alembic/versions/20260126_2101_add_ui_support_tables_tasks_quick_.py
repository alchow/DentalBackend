"""Add UI support tables tasks quick_phrases and columns

Revision ID: 77ce00cb2f5e
Revises: 9a2457a6290f
Create Date: 2026-01-26 21:01:08.322757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77ce00cb2f5e'
down_revision: Union[str, None] = '9a2457a6290f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade() -> None:
    # 1. Add 'medical_history' to 'patients'
    op.add_column('patients', sa.Column('medical_history', JSONB, nullable=True))

    # 2. Add 'note_type' to 'notes' and 'note_history'
    op.add_column('notes', sa.Column('note_type', sa.String(), nullable=True, server_default='GENERAL'))
    op.add_column('note_history', sa.Column('note_type', sa.String(), nullable=True))

    # 3. Add 'summary' to 'visits'
    op.add_column('visits', sa.Column('summary', JSONB, nullable=True))

    # 4. Create 'tasks' table
    op.create_table(
        'tasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', UUID(as_uuid=True), sa.ForeignKey('patients.id'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'), # PENDING, COMPLETED, DISMISSED
        sa.Column('priority', sa.String(), nullable=False, server_default='NORMAL'), # HIGH, NORMAL
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('generated_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # 5. Create 'quick_phrases' table
    op.create_table(
        'quick_phrases',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('usage_count', sa.Integer(), server_default='0'),
    )


def downgrade() -> None:
    op.drop_table('quick_phrases')
    op.drop_table('tasks')
    op.drop_column('visits', 'summary')
    op.drop_column('note_history', 'note_type')
    op.drop_column('notes', 'note_type')
    op.drop_column('patients', 'medical_history')
