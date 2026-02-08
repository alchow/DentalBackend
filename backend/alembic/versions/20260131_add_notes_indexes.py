"""Add performance indexes for notes list endpoint

Revision ID: 20260131_add_notes_indexes
Revises: 
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20260131_add_notes_indexes'
down_revision = 'add_search_duration'  # Chain after the latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes for note list endpoint performance."""
    # Index for sorting by created_at (most common sort)
    op.create_index(
        'ix_notes_created_at',
        'notes',
        ['created_at'],
        unique=False,
        postgresql_using='btree'
    )
    
    # Index for filtering by note_type
    op.create_index(
        'ix_notes_note_type',
        'notes',
        ['note_type'],
        unique=False
    )
    
    # Index for filtering by visit_id
    op.create_index(
        'ix_notes_visit_id',
        'notes',
        ['visit_id'],
        unique=False
    )
    
    # Composite index for common query pattern: office_id + created_at
    op.create_index(
        'ix_notes_office_created',
        'notes',
        ['office_id', 'created_at'],
        unique=False,
        postgresql_using='btree'
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_notes_office_created', table_name='notes')
    op.drop_index('ix_notes_visit_id', table_name='notes')
    op.drop_index('ix_notes_note_type', table_name='notes')
    op.drop_index('ix_notes_created_at', table_name='notes')
