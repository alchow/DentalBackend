import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String, index=True, nullable=False) # Store only hash of the key
    prefix = Column(String, nullable=False) # e.g. "sk_live_1234..." for UI display/identification
    name = Column(String, nullable=True) # e.g. "Zapier Integration"
    
    office_id = Column(UUID(as_uuid=True), ForeignKey("offices.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    office = relationship("Office", back_populates="api_keys")
