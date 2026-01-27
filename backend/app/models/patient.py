from sqlalchemy import Column, String, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String, nullable=False) # Encrypted in app
    last_name = Column(String, nullable=False)  # Encrypted in app
    last_name_hash = Column(String, index=True, nullable=False) # Blind Index for search
    dob = Column(Date, nullable=False)
    contact_info = Column(JSONB, nullable=True) # Encrypted JSON
    medical_history = Column(JSONB, nullable=True) # Allergies, Meds (JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    visits = relationship("Visit", back_populates="patient")
    notes = relationship("Note", back_populates="patient")
    bills = relationship("Bill", back_populates="patient")
