"""Add dental columns area tooth surface

Revision ID: 9a2457a6290f
Revises: 335f68fd249c
Create Date: 2026-01-22 22:40:54.536792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a2457a6290f'
down_revision: Union[str, None] = '335f68fd249c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove old 'tooth' column
    op.drop_column('notes', 'tooth')
    op.drop_column('note_history', 'tooth')

    # Add new structured columns to 'notes'
    op.add_column('notes', sa.Column('area_of_oral_cavity', sa.String(), nullable=True))
    op.add_column('notes', sa.Column('tooth_number', sa.String(), nullable=True))
    op.add_column('notes', sa.Column('surface_ids', sa.String(), nullable=True))

    # Add new structured columns to 'note_history'
    op.add_column('note_history', sa.Column('area_of_oral_cavity', sa.String(), nullable=True))
    op.add_column('note_history', sa.Column('tooth_number', sa.String(), nullable=True))
    op.add_column('note_history', sa.Column('surface_ids', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove new columns from 'note_history'
    op.drop_column('note_history', 'surface_ids')
    op.drop_column('note_history', 'tooth_number')
    op.drop_column('note_history', 'area_of_oral_cavity')

    # Remove new columns from 'notes'
    op.drop_column('notes', 'surface_ids')
    op.drop_column('notes', 'tooth_number')
    op.drop_column('notes', 'area_of_oral_cavity')

    # Restore old column
    op.add_column('note_history', sa.Column('tooth', sa.String(), nullable=True))
    op.add_column('notes', sa.Column('tooth', sa.String(), nullable=True))
