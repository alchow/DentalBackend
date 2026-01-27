from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default='PENDING') # PENDING, COMPLETED, DISMISSED
    priority = Column(String, nullable=False, default='NORMAL') # HIGH, NORMAL
    due_date = Column(Date, nullable=True)
    generated_by = Column(String, nullable=True) # LLM or User
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
