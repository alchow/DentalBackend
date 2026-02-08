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
    DELETED = "DELETED"  # Soft delete for mistakes

class VisitBase(BaseModel):
    visit_date: datetime
    reason: Optional[str] = None
    status: VisitStatus = VisitStatus.SCHEDULED
    duration_minutes: Optional[int] = 30  # Default 30 min appointment
    patient_id: UUID

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    visit_date: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[VisitStatus] = None
    duration_minutes: Optional[int] = None

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
    note_type: str = "GENERAL"
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
    note_type: Optional[str] = None
    author_id: str # Confirm identity

class NoteResponse(NoteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Pagination & Extended Schemas (Added 2026-01-31) ---

class PatientEmbed(BaseModel):
    """Lightweight patient info for embedding in note responses."""
    id: UUID
    first_name: str
    last_name: str
    dob: datetime

    class Config:
        from_attributes = True


class NoteWithPatient(NoteResponse):
    """Note response with optional embedded patient data."""
    patient: Optional[PatientEmbed] = None


class NoteListResponse(BaseModel):
    """Paginated response for note list endpoint."""
    items: list
    total: int
    limit: int
    offset: int


# --- Note History Schemas (Added 2026-02-01) ---

class NoteHistoryItem(BaseModel):
    """A single version from note edit history."""
    id: UUID
    previous_content: str  # Decrypted at API layer
    edited_by: Optional[str] = None
    change_reason: Optional[str] = None
    created_at: datetime
    tooth_number: Optional[str] = None
    surface_ids: Optional[str] = None
    area_of_oral_cavity: Optional[str] = None
    note_type: Optional[str] = None

    class Config:
        from_attributes = True


class NoteHistoryListResponse(BaseModel):
    """Response for GET /notes/{id}/history endpoint."""
    items: list[NoteHistoryItem]
    total: int
