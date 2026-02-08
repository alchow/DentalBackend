"""Internal endpoints - Not exposed to public API.

These endpoints are called by Cloud Tasks and other internal services.
"""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel

from app.db.session import get_db
from app.services.summary_service import SummaryService

logger = logging.getLogger(__name__)

router = APIRouter()

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")


class GenerateSummaryRequest(BaseModel):
    patient_id: str
    note_id: str
    office_id: str


async def verify_internal_key(x_internal_key: str = Header(...)):
    """Verify the shared internal API key from Cloud Tasks.
    
    TODO: Migrate to OIDC token verification for proper Cloud Tasks auth.
    """
    if not INTERNAL_API_KEY:
        raise HTTPException(status_code=503, detail="Internal endpoint not configured")
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid internal key")


@router.post("/generate-summary")
async def generate_summary(
    request: GenerateSummaryRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_internal_key)
):
    """Internal endpoint for Cloud Tasks to trigger summary generation.
    
    Requires X-Internal-Key header for authentication.
    """
    logger.info(f"Received summary request: patient={request.patient_id}, note={request.note_id}")
    
    service = SummaryService(db)
    
    try:
        result = await service.generate_patient_summary(
            patient_id=UUID(request.patient_id),
            triggered_by_note_id=UUID(request.note_id),
            office_id=UUID(request.office_id)
        )
        
        if result:
            logger.info(f"Summary created: id={result.id}, patient={request.patient_id}")
            return {"status": "success", "summary_id": str(result.id)}
        else:
            logger.warning(f"Summary skipped for patient={request.patient_id}: No recent notes")
            return {"status": "skipped", "reason": "No recent notes found"}
            
    except Exception as e:
        logger.error(f"Summary generation failed for patient={request.patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Summary generation failed")
