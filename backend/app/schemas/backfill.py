"""Backfill schemas for historical data import.

Each schema extends the base create schema but adds a required created_at field
and validates that the timestamp is not in the future.
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID

from app.schemas.visit_note import NoteCreate, VisitCreate
from app.schemas.patient import PatientCreate
from app.schemas.bill import BillCreate


class BackfillMixin(BaseModel):
    """Mixin that adds created_at with past-date validation."""
    created_at: datetime
    
    @field_validator('created_at')
    @classmethod
    def created_at_must_be_past(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        # Make v timezone-aware if naive
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v > now:
            raise ValueError('created_at must not be in the future')
        return v


class NoteBackfillCreate(NoteCreate, BackfillMixin):
    """Create a note with custom created_at for backfill."""
    pass


class PatientBackfillCreate(PatientCreate, BackfillMixin):
    """Create a patient with custom created_at for backfill."""
    pass


class VisitBackfillCreate(VisitCreate, BackfillMixin):
    """Create a visit with custom created_at for backfill."""
    pass


class BillBackfillCreate(BillCreate, BackfillMixin):
    """Create a bill with custom created_at for backfill."""
    pass


# Response schemas with is_backfilled flag
class BackfillResponse(BaseModel):
    """Standard response for backfill operations."""
    id: UUID
    created_at: datetime
    is_backfilled: bool = True
    
    class Config:
        from_attributes = True
