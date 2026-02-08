from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base


class PatientSummary(Base):
    """AI-generated or manually created patient summary with history."""
    __tablename__ = "patient_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Content (Fernet encrypted JSON)
    content_encrypted = Column(Text, nullable=False)
    
    # Metadata
    source = Column(String(20), nullable=False)  # 'AI' or 'MANUAL'
    model_provider = Column(String(20), nullable=True)  # openai, gemini, anthropic
    model_name = Column(String(50), nullable=True)
    prompt_version = Column(String(20), nullable=True)  # v1, v2, etc.
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0
    
    # Audit
    triggered_by_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=True)
    edited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes_context = Column(JSONB, nullable=True)  # IDs of notes used for context
    
    # Timestamps & Tenant
    created_at = Column(DateTime(timezone=True), default=func.now())
    office_id = Column(UUID(as_uuid=True), ForeignKey("offices.id"), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="summaries")
