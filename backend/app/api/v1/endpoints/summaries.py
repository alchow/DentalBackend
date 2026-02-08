"""Summary API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_tenant_id, get_current_user
from app.services.summary_service import SummaryService
from app.schemas.summary import SummaryCreate, SummaryResponse, SummaryHistoryResponse

router = APIRouter()


@router.get("/{patient_id}/summary", response_model=SummaryResponse)
async def get_patient_summary(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get the latest summary for a patient."""
    service = SummaryService(db)
    summary = await service.get_latest_summary(patient_id, tenant_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="No summary found for this patient")
    
    return summary


@router.get("/{patient_id}/summary/history", response_model=SummaryHistoryResponse)
async def get_summary_history(
    patient_id: UUID,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get paginated summary history for a patient."""
    if limit > 100:
        limit = 100
    
    service = SummaryService(db)
    return await service.get_summary_history(patient_id, limit, offset, tenant_id)


@router.put("/{patient_id}/summary", response_model=SummaryResponse)
async def update_patient_summary(
    patient_id: UUID,
    summary_data: SummaryCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user = Depends(get_current_user)
):
    """Manually create or edit a patient summary."""
    service = SummaryService(db)
    
    return await service.save_manual_summary(
        patient_id=patient_id,
        content=summary_data.content,
        user_id=user.id,
        office_id=tenant_id
    )
