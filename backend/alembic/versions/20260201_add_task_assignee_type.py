"""Add assignee_type to tasks

Revision ID: 8b3c4d5e6f7a
Revises: 20260201_add_ssn_fields
Create Date: 2026-02-01 17:58:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b3c4d5e6f7a'
down_revision: Union[str, None] = '20260201_add_ssn_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add assignee_type column with default 'DENTIST'
    # Values: DENTIST, PATIENT, FRONT_DESK
    op.add_column('tasks', sa.Column('assignee_type', sa.String(), nullable=False, server_default='DENTIST'))


def downgrade() -> None:
    op.drop_column('tasks', 'assignee_type')
