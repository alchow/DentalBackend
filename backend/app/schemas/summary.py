from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class SummaryContent(BaseModel):
    """Structured summary content.
    
    For AI summaries: summary_markdown contains the full narrative.
    For MANUAL summaries: legacy fields are used.
    """
    # AI-generated content (v2 prompt returns markdown)
    summary_markdown: Optional[str] = None
    
    # Legacy/manual summary fields
    chief_concerns: Optional[List[str]] = None
    recent_procedures: Optional[List[str]] = None
    ongoing_treatment: Optional[str] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    notes_summary: Optional[str] = None
    
    # Additional structured fields from AI (extracted from markdown)
    key_clinical_findings: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None


class SummaryCreate(BaseModel):
    """Request to manually create/edit a summary."""
    content: SummaryContent


class SummaryResponse(BaseModel):
    """Summary response."""
    id: UUID
    patient_id: UUID
    content: SummaryContent
    source: str  # 'AI' or 'MANUAL'
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    edited_by: Optional[UUID] = None
    
    class Config:
        from_attributes = True


class SummaryHistoryResponse(BaseModel):
    """Paginated summary history response."""
    items: List[SummaryResponse]
    total: int
    limit: int
    offset: int
