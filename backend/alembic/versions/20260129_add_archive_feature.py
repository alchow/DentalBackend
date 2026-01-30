"""add_archive_columns_to_users_and_offices

Revision ID: 20260129_add_archive_feature
Revises: 20260129_add_deleted_to_visitstatus
Create Date: 2026-01-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20260129_add_archive_feature'
down_revision = '20260129_add_deleted_to_visitstatus'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add archive columns to offices table
    op.add_column('offices', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('offices', sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('offices', sa.Column('archived_by', postgresql.UUID(as_uuid=True), nullable=True))
    
    # 2. Add archive columns to users table
    op.add_column('users', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True))
    
    # 3. Drop the existing unique constraint on email
    # Note: The constraint name may vary; adjust if needed
    op.drop_constraint('users_email_key', 'users', type_='unique')
    
    # 4. Create partial unique index - only active (non-archived) users must have unique email
    op.execute("""
        CREATE UNIQUE INDEX users_email_active_unique 
        ON users (email) 
        WHERE is_archived = FALSE
    """)


def downgrade() -> None:
    # 1. Drop the partial unique index
    op.execute("DROP INDEX IF EXISTS users_email_active_unique")
    
    # 2. Recreate the original unique constraint
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    
    # 3. Remove archive columns from users
    op.drop_column('users', 'archived_at')
    op.drop_column('users', 'is_archived')
    
    # 4. Remove archive columns from offices
    op.drop_column('offices', 'archived_by')
    op.drop_column('offices', 'archived_at')
    op.drop_column('offices', 'is_archived')
