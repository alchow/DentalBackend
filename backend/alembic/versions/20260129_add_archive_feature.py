"""add_archive_columns_to_users_and_offices

Revision ID: 20260129_add_archive_feature
Revises: add_deleted_enum
Create Date: 2026-01-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_archive_feature'
down_revision = 'add_deleted_enum'
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
    
    # 3. Drop the existing unique constraint/index on email (may be constraint OR index)
    # Use raw SQL to handle both cases safely
    op.execute("""
        DO $$
        BEGIN
            -- Try to drop the unique constraint first
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'users_email_key') THEN
                ALTER TABLE users DROP CONSTRAINT users_email_key;
            END IF;
            -- Also try to drop the unique index (created by multi-tenancy migration)
            IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_users_email') THEN
                DROP INDEX ix_users_email;
            END IF;
        END $$;
    """)
    
    # 4. Create partial unique index - only active (non-archived) users must have unique email
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS users_email_active_unique 
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
