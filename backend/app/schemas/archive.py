from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ArchiveOfficeRequest(BaseModel):
    """Request to archive an office and all associated data."""
    reason: Optional[str] = None  # Audit trail / reason for archiving


class ArchiveOfficeResponse(BaseModel):
    """Response after archiving an office."""
    success: bool
    office_id: UUID
    office_name: str
    archived_at: datetime
    users_archived: int
    message: str
