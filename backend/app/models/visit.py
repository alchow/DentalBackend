from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
import enum

from app.db.base_class import Base

class VisitStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DELETED = "DELETED"  # Soft delete for mistakes

class Visit(Base):
    __tablename__ = "visits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    visit_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String, nullable=True)
    status = Column(Enum(VisitStatus), default=VisitStatus.SCHEDULED, nullable=False)
    duration_minutes = Column(Integer, nullable=True, default=30) # Standard appointment length
    
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    office_id = Column(UUID(as_uuid=True), ForeignKey("offices.id"), nullable=True)
    is_backfilled = Column(Boolean, default=False, nullable=False)

    patient = relationship("Patient", back_populates="visits")
    notes = relationship("Note", back_populates="visit")
    bills = relationship("Bill", back_populates="visit")
