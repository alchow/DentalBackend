from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models import Note, NoteHistory, User
from app.schemas import visit_note as schemas
from app.core.security import encrypt_data, decrypt_data
from app.api.deps import get_current_tenant_id, get_current_user

router = APIRouter()

@router.post("", response_model=schemas.NoteResponse)
async def create_note(
    note: schemas.NoteCreate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    encrypted_content = encrypt_data(note.content)
    
    db_note = Note(
        patient_id=note.patient_id,
        visit_id=note.visit_id,
        content=encrypted_content,
        area_of_oral_cavity=note.area_of_oral_cavity,
        tooth_number=note.tooth_number,
        surface_ids=note.surface_ids,
        note_type=note.note_type,
        author_id=current_user.email, # Use authenticated user email/name as author
        office_id=tenant_id
    )
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    
    # Index Note for Search
    from app.services.search_service import SearchService
    search_service = SearchService(db)
    await search_service.index_note(db_note.id, note.content)
    
    db_note.content = note.content # Return decrypted
    return db_note

@router.put("/{note_id}", response_model=schemas.NoteResponse)
async def update_note(
    note_id: UUID, 
    note_update: schemas.NoteUpdate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Note).filter(Note.id == note_id, Note.office_id == tenant_id))
    db_note = result.scalars().first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # 1. Create History Record with OLD content
    history_record = NoteHistory(
        note_id=db_note.id,
        previous_content=db_note.content, # Already encrypted
        area_of_oral_cavity=db_note.area_of_oral_cavity,
        tooth_number=db_note.tooth_number,
        surface_ids=db_note.surface_ids,
        note_type=db_note.note_type,
        edited_by=current_user.email, # Use authenticated user
        change_reason="Update",
        office_id=tenant_id
    )
    db.add(history_record)
    
    # 2. Update Note with NEW content
    db_note.content = encrypt_data(note_update.content)
    db_note.area_of_oral_cavity = note_update.area_of_oral_cavity
    db_note.tooth_number = note_update.tooth_number
    db_note.surface_ids = note_update.surface_ids
    if note_update.note_type:
        db_note.note_type = note_update.note_type
    
    # Helper logic: Note author usually stays the same, or we track "last_edited_by" in a separate column if model supports it.
    # Note model has `updated_at`. `author_id` is usually the creator.
    # We won't change `author_id` here unless business req says so. 
    # But for now, let's leave author_id as creator.
    
    # Index Update for Search
    from app.services.search_service import SearchService
    search_service = SearchService(db)
    await search_service.index_note(db_note.id, note_update.content)
    
    await db.commit()
    await db.refresh(db_note)
    
    db_note.content = note_update.content # Return decrypted
    return db_note

@router.get("/patient/{patient_id}", response_model=List[schemas.NoteResponse])
async def read_patient_notes(
    patient_id: UUID, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(Note).filter(Note.patient_id == patient_id, Note.office_id == tenant_id))
    notes = result.scalars().all()
    
    for n in notes:
        n.content = decrypt_data(n.content)
        
    return notes
