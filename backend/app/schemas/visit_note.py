from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class VisitStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class VisitBase(BaseModel):
    visit_date: datetime
    reason: Optional[str] = None
    status: VisitStatus = VisitStatus.SCHEDULED
    patient_id: UUID

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    visit_date: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[VisitStatus] = None

class VisitResponse(VisitBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    content: str
    area_of_oral_cavity: Optional[str] = None
    tooth_number: Optional[str] = None
    surface_ids: Optional[str] = None
    author_id: str
    patient_id: UUID
    visit_id: Optional[UUID] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    content: str # Always require full content for update logic implementation
    area_of_oral_cavity: Optional[str] = None
    tooth_number: Optional[str] = None
    surface_ids: Optional[str] = None
    author_id: str # Confirm identity

class NoteResponse(NoteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
