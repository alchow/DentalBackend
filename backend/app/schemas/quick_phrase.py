from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class QuickPhraseBase(BaseModel):
    text: str
    category: Optional[str] = None

class QuickPhraseCreate(QuickPhraseBase):
    pass

class QuickPhraseUpdate(BaseModel):
    text: Optional[str] = None
    category: Optional[str] = None
    usage_count: Optional[int] = None

class QuickPhraseResponse(QuickPhraseBase):
    id: UUID
    usage_count: int

    class Config:
        from_attributes = True
