from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base

class QuickPhrase(Base):
    __tablename__ = "quick_phrases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    text = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    usage_count = Column(Integer, server_default='0')
