"""Summary Service - Business logic for patient summary generation and storage."""
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from uuid import UUID

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc

from app.models.patient_summary import PatientSummary
from app.models.note import Note
from app.core.security import encrypt_data, decrypt_data
from app.services.llm_service import get_llm_provider, load_prompt, SummaryResult
from app.schemas.summary import SummaryContent, SummaryResponse, SummaryHistoryResponse


class SummaryService:
    """Service for managing patient summaries."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_latest_summary(self, patient_id: UUID, office_id: UUID = None) -> Optional[SummaryResponse]:
        """Get the most recent summary for a patient."""
        query = select(PatientSummary).filter(PatientSummary.patient_id == patient_id)
        if office_id:
            query = query.filter(PatientSummary.office_id == office_id)
        result = await self.db.execute(
            query.order_by(desc(PatientSummary.created_at)).limit(1)
        )
        summary = result.scalars().first()
        
        if not summary:
            return None
        
        return self._to_response(summary)
    
    async def get_summary_history(
        self, 
        patient_id: UUID, 
        limit: int = 20, 
        offset: int = 0,
        office_id: UUID = None
    ) -> SummaryHistoryResponse:
        """Get paginated summary history for a patient."""
        # Get total count
        count_query = select(func.count(PatientSummary.id)).filter(PatientSummary.patient_id == patient_id)
        if office_id:
            count_query = count_query.filter(PatientSummary.office_id == office_id)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Get paginated results
        history_query = select(PatientSummary).filter(PatientSummary.patient_id == patient_id)
        if office_id:
            history_query = history_query.filter(PatientSummary.office_id == office_id)
        result = await self.db.execute(
            history_query
            .order_by(desc(PatientSummary.created_at))
            .limit(limit)
            .offset(offset)
        )
        summaries = result.scalars().all()
        
        return SummaryHistoryResponse(
            items=[self._to_response(s) for s in summaries],
            total=total,
            limit=limit,
            offset=offset
        )
    
    async def save_manual_summary(
        self, 
        patient_id: UUID, 
        content: SummaryContent, 
        user_id: UUID,
        office_id: UUID
    ) -> SummaryResponse:
        """Save a manually created/edited summary."""
        content_json = content.model_dump(exclude_none=True)
        encrypted = encrypt_data(json.dumps(content_json))
        
        summary = PatientSummary(
            patient_id=patient_id,
            content_encrypted=encrypted,
            source="MANUAL",
            edited_by=user_id,
            office_id=office_id
        )
        
        logger.info(f"Manual summary saved for patient_id={patient_id}")
        
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)
        
        return self._to_response(summary)
    
    async def generate_patient_summary(
        self, 
        patient_id: UUID,
        triggered_by_note_id: Optional[UUID],
        office_id: UUID
    ) -> SummaryResponse:
        """Generate AI summary from patient notes."""
        # Get notes: latest + past 7 days
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Query notes by patient_id only - office scoping handled at patient creation level
        result = await self.db.execute(
            select(Note)
            .filter(
                Note.patient_id == patient_id,
                Note.created_at >= seven_days_ago
            )
            .order_by(desc(Note.created_at))
        )
        notes = result.scalars().all()
        
        if not notes:
            # No recent notes, skip generation
            return None
        
        # Decrypt note contents and add date context
        note_texts = []
        note_ids = []
        for note in notes:
            try:
                content = decrypt_data(note.content)
                date_str = note.created_at.strftime("%Y-%m-%d")
                note_texts.append(f"[{date_str}] {content}")
                note_ids.append(str(note.id))
            except Exception:
                continue
        
        if not note_texts:
            return None
        
        # Load prompt and generate
        prompt_content, prompt_version = load_prompt("patient_summary")
        provider = get_llm_provider()
        
        llm_result = await provider.generate_summary(note_texts, prompt_content)
        llm_result.prompt_version = prompt_version
        
        # Encrypt and save
        encrypted = encrypt_data(json.dumps(llm_result.content))
        
        summary = PatientSummary(
            patient_id=patient_id,
            content_encrypted=encrypted,
            source="AI",
            model_provider=llm_result.model_provider,
            model_name=llm_result.model_name,
            prompt_version=llm_result.prompt_version,
            confidence_score=llm_result.confidence_score,
            triggered_by_note_id=triggered_by_note_id,
            notes_context={"note_ids": note_ids},
            office_id=office_id
        )
        
        logger.info(f"AI summary saved for patient_id={patient_id}, model={llm_result.model_name}")
        
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)
        
        return self._to_response(summary)
    
    def _to_response(self, summary: PatientSummary) -> SummaryResponse:
        """Convert model to response schema."""
        content_json = json.loads(decrypt_data(summary.content_encrypted))
        
        return SummaryResponse(
            id=summary.id,
            patient_id=summary.patient_id,
            content=SummaryContent(**content_json),
            source=summary.source,
            model_provider=summary.model_provider,
            model_name=summary.model_name,
            prompt_version=summary.prompt_version,
            confidence_score=summary.confidence_score,
            created_at=summary.created_at,
            edited_by=summary.edited_by
        )
