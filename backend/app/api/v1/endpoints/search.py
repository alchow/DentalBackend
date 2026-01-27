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

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 10

@router.post("", response_model=List[schemas.NoteResponse])
async def search_notes(query: SearchQuery, db: AsyncSession = Depends(get_db)):
    service = SearchService(db)
    note_ids = await service.search_notes(query.query, query.limit)
    
    if not note_ids:
        return []
        
    # Fetch full notes
    # We must decrypt them before returning
    stmt = select(Note).filter(Note.id.in_(note_ids))
    result = await db.execute(stmt)
    notes = result.scalars().all()
    
    # Decrypt
    # TODO: In future, return snippet highlighting instead of full content?
    for n in notes:
        n.content = decrypt_data(n.content)
        
    return notes
