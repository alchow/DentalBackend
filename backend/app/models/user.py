import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="DENTIST") # ADMIN, DENTIST, HYGIENIST, STAFF
    is_active = Column(Boolean, default=True)
    
    office_id = Column(UUID(as_uuid=True), ForeignKey("offices.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    office = relationship("Office", back_populates="users")
