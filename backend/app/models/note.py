from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.db.base_class import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("visits.id"), nullable=True) # Optional
    content = Column(Text, nullable=False) # Encrypted
    area_of_oral_cavity = Column(String, nullable=True)
    tooth_number = Column(String, nullable=True)
    surface_ids = Column(String, nullable=True)
    note_type = Column(String, nullable=True, default="GENERAL") # Added for UI tabs
    author_id = Column(String, nullable=True) # Provider ID
    
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    office_id = Column(UUID(as_uuid=True), ForeignKey("offices.id"), nullable=True)

    patient = relationship("Patient", back_populates="notes")
    visit = relationship("Visit", back_populates="notes")
    history = relationship("NoteHistory", back_populates="note", cascade="all, delete-orphan")

class NoteHistory(Base):
    __tablename__ = "note_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False)
    previous_content = Column(Text, nullable=False) # Encrypted
    area_of_oral_cavity = Column(String, nullable=True)
    tooth_number = Column(String, nullable=True)
    surface_ids = Column(String, nullable=True)
    note_type = Column(String, nullable=True) # Snapshot
    edited_by = Column(String, nullable=True) # User ID or Name
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    change_reason = Column(String, nullable=True)

    office_id = Column(UUID(as_uuid=True), ForeignKey("offices.id"), nullable=True)

    note = relationship("Note", back_populates="history")
