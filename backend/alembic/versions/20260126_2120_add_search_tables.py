"""Add search tables note_embeddings and blind_indexes

Revision ID: 88de01cb3f6e
Revises: 77ce00cb2f5e
Create Date: 2026-01-26 21:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '88de01cb3f6e'
down_revision: Union[str, None] = '77ce00cb2f5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 2. Create note_embeddings table
    op.create_table(
        'note_embeddings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('note_id', UUID(as_uuid=True), sa.ForeignKey('notes.id'), nullable=False, unique=True),
        sa.Column('vector', Vector(1536), nullable=True),
    )
    # Add HNSW index for faster vector search (Euclidean distance typically)
    # op.execute("CREATE INDEX ON note_embeddings USING hnsw (vector vector_l2_ops)")
    # Commented out for now to ensure compatibility with all Postgres versions without extra config

    # 3. Create blind_indexes table
    op.create_table(
        'blind_indexes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('note_id', UUID(as_uuid=True), sa.ForeignKey('notes.id'), nullable=False),
        sa.Column('term_hash', sa.String(), nullable=False),
    )
    op.create_index('ix_blind_indexes_term_hash', 'blind_indexes', ['term_hash'])


def downgrade() -> None:
    op.drop_index('ix_blind_indexes_term_hash', table_name='blind_indexes')
    op.drop_table('blind_indexes')
    op.drop_table('note_embeddings')
    # op.execute("DROP EXTENSION vector") # Generally bad practice to drop extensions in migrations as other apps might use them
