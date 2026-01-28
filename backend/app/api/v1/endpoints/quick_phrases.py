from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models import QuickPhrase
from app.schemas import quick_phrase as schemas
from app.api.deps import get_current_tenant_id

router = APIRouter()

@router.post("", response_model=schemas.QuickPhraseResponse)
async def create_quick_phrase(
    phrase: schemas.QuickPhraseCreate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    db_phrase = QuickPhrase(
        text=phrase.text,
        category=phrase.category,
        office_id=tenant_id
    )
    db.add(db_phrase)
    await db.commit()
    await db.refresh(db_phrase)
    return db_phrase

@router.get("", response_model=List[schemas.QuickPhraseResponse])
async def read_quick_phrases(
    category: str = None, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    query = select(QuickPhrase).filter(QuickPhrase.office_id == tenant_id)
    if category:
        query = query.filter(QuickPhrase.category == category)
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/{phrase_id}", response_model=schemas.QuickPhraseResponse)
async def update_quick_phrase(
    phrase_id: UUID, 
    phrase_update: schemas.QuickPhraseUpdate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(QuickPhrase).filter(QuickPhrase.id == phrase_id, QuickPhrase.office_id == tenant_id))
    db_phrase = result.scalars().first()
    if not db_phrase:
        raise HTTPException(status_code=404, detail="Quick Phrase not found")

    if phrase_update.text:
        db_phrase.text = phrase_update.text
    if phrase_update.category:
        db_phrase.category = phrase_update.category
    if phrase_update.usage_count is not None:
        db_phrase.usage_count = phrase_update.usage_count

    await db.commit()
    await db.refresh(db_phrase)
    return db_phrase

@router.delete("/{phrase_id}", status_code=204)
async def delete_quick_phrase(
    phrase_id: UUID, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(QuickPhrase).filter(QuickPhrase.id == phrase_id, QuickPhrase.office_id == tenant_id))
    db_phrase = result.scalars().first()
    if not db_phrase:
        raise HTTPException(status_code=404, detail="Quick Phrase not found")
    
    await db.delete(db_phrase)
    await db.commit()
