from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from app.db.session import get_db
from app.services.search_service import SearchService
from app.models import Note
from app.schemas import visit_note as schemas
from app.core.security import decrypt_data
from sqlalchemy import select
from app.api.deps import get_current_tenant_id

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 10

@router.post("", response_model=List[schemas.NoteResponse])
async def search_notes(
    query: SearchQuery, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    service = SearchService(db)
    note_ids = await service.search_notes(query.query, tenant_id=tenant_id, limit=query.limit)
    
    if not note_ids:
        return []
        
    # Fetch full notes
    # We must decrypt them before returning
    # Also enforce tenant filter here just in case, though search service should have handled it.
    stmt = select(Note).filter(Note.id.in_(note_ids), Note.office_id == tenant_id)
    result = await db.execute(stmt)
    notes = result.scalars().all()
    
    # Decrypt
    # TODO: In future, return snippet highlighting instead of full content?
    for n in notes:
        n.content = decrypt_data(n.content)
        
    return notes
