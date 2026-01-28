import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base

class Office(Base):
    __tablename__ = "offices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    # Relationships
    users = relationship("User", back_populates="office")
    api_keys = relationship("ApiKey", back_populates="office")
    # We can add relationships to other models (patients, etc.) later if needed for cascading
