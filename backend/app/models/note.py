from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("visits.id"), nullable=True) # Optional
    content = Column(Text, nullable=False) # Encrypted
    tooth = Column(String, nullable=True) # Metadata: "19", "FM"
    author_id = Column(String, nullable=False) # Provider ID
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    patient = relationship("Patient", back_populates="notes")
    visit = relationship("Visit", back_populates="notes")
    history = relationship("NoteHistory", back_populates="note", cascade="all, delete-orphan")

class NoteHistory(Base):
    __tablename__ = "note_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False)
    previous_content = Column(Text, nullable=False) # Encrypted
    tooth = Column(String, nullable=True) # Snapshot of tooth at time of edit
    edited_by = Column(String, nullable=False) # User ID
    edited_at = Column(DateTime(timezone=True), server_default=func.now())
    change_reason = Column(String, nullable=True)

    note = relationship("Note", back_populates="history")
