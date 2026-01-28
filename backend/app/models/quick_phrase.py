from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base

class QuickPhrase(Base):
    __tablename__ = "quick_phrases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    text = Column(String, nullable=False)
    category = Column(String, index=True)
    usage_count = Column(Integer, default=0)
    
    office_id = Column(UUID(as_uuid=True), ForeignKey("offices.id"), nullable=True)
