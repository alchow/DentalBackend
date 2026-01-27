from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.db.base_class import Base

class NoteEmbedding(Base):
    __tablename__ = "note_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False, unique=True)
    vector = Column(Vector(1536)) # OpenAI dimension
    
    # We treat the vector index creation in Alembic migration manually usually, or here.
    # For now, just definition.

class BlindIndex(Base):
    """
    Stores hashes of keywords for exact lookup of encrypted data.
    One note -> Many keywords (Many-to-Many effectively, but flattened here).
    """
    __tablename__ = "blind_indexes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False)
    term_hash = Column(String, index=True, nullable=False) # HMAC-SHA256 of the word
