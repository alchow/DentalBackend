from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, desc, asc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.models import Note, NoteHistory, User, Patient
from app.schemas import visit_note as schemas
from app.core.security import encrypt_data, decrypt_data
from app.api.deps import get_current_tenant_id, get_current_user


router = APIRouter()


def _build_note_dict(note, include_patient=False):
    """Build a dict from Note model to avoid lazy loading issues."""
    note_dict = {
        "id": note.id,
        "content": decrypt_data(note.content),
        "area_of_oral_cavity": note.area_of_oral_cavity,
        "tooth_number": note.tooth_number,
        "surface_ids": note.surface_ids,
        "note_type": note.note_type,
        "author_id": note.author_id,
        "patient_id": note.patient_id,
        "visit_id": note.visit_id,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }
    
    # Only include patient if explicitly requested AND it was eager-loaded
    if include_patient and hasattr(note, 'patient') and note.patient is not None:
        note_dict["patient"] = {
            "id": note.patient.id,
            "first_name": decrypt_data(note.patient.first_name),
            "last_name": decrypt_data(note.patient.last_name),
            "dob": note.patient.dob,
        }
    else:
        note_dict["patient"] = None
    
    return note_dict


# --- List All Notes (WP-2) ---
@router.get("", response_model=schemas.NoteListResponse)
async def list_notes(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    note_type: Optional[str] = None,
    patient_id: Optional[UUID] = None,
    visit_id: Optional[UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    include_patient: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List all notes for the office with filtering and pagination."""
    # Base query with tenant isolation
    query = select(Note).filter(Note.office_id == tenant_id)
    count_query = select(func.count(Note.id)).filter(Note.office_id == tenant_id)
    
    # Apply filters
    if note_type:
        query = query.filter(Note.note_type == note_type)
        count_query = count_query.filter(Note.note_type == note_type)
    if patient_id:
        query = query.filter(Note.patient_id == patient_id)
        count_query = count_query.filter(Note.patient_id == patient_id)
    if visit_id:
        query = query.filter(Note.visit_id == visit_id)
        count_query = count_query.filter(Note.visit_id == visit_id)
    if date_from:
        query = query.filter(Note.created_at >= date_from)
        count_query = count_query.filter(Note.created_at >= date_from)
    if date_to:
        query = query.filter(Note.created_at <= date_to)
        count_query = count_query.filter(Note.created_at <= date_to)
    
    # Eager load patient if requested
    if include_patient:
        query = query.options(selectinload(Note.patient))
    
    # Apply sorting
    sort_column = getattr(Note, sort, Note.created_at)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute queries
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    result = await db.execute(query)
    notes = result.scalars().all()
    
    # Build response items as dicts to avoid lazy loading issues
    items = [_build_note_dict(n, include_patient) for n in notes]
    
    return schemas.NoteListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


# --- Get Single Note (WP-3) ---
@router.get("/{note_id}", response_model=schemas.NoteWithPatient)
async def get_note(
    note_id: UUID,
    include_patient: bool = Query(False),
    include_visit: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get a single note by ID."""
    query = select(Note).filter(Note.id == note_id)
    
    # Always eager load if requested to avoid async issues
    if include_patient:
        query = query.options(selectinload(Note.patient))
    if include_visit:
        query = query.options(selectinload(Note.visit))
    
    result = await db.execute(query)
    db_note = result.scalars().first()
    
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check tenant access
    if str(db_note.office_id) != str(tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Build response dict to avoid lazy loading issues
    return _build_note_dict(db_note, include_patient)


# --- Get Note History (Added 2026-02-01) ---
@router.get("/{note_id}/history", response_model=schemas.NoteHistoryListResponse)
async def get_note_history(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Get edit history for a note.
    
    Returns all previous versions of the note, ordered newest-first.
    Content is automatically decrypted.
    """
    # First verify the note exists and belongs to this tenant
    note_result = await db.execute(select(Note).filter(Note.id == note_id))
    db_note = note_result.scalars().first()
    
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if str(db_note.office_id) != str(tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all history entries for this note, newest first
    history_query = (
        select(NoteHistory)
        .filter(NoteHistory.note_id == note_id)
        .order_by(desc(NoteHistory.created_at))
    )
    
    result = await db.execute(history_query)
    history_entries = result.scalars().all()
    
    # Build response with decrypted content
    items = []
    for entry in history_entries:
        items.append({
            "id": entry.id,
            "previous_content": decrypt_data(entry.previous_content),
            "edited_by": entry.edited_by,
            "change_reason": entry.change_reason,
            "created_at": entry.created_at,
            "tooth_number": entry.tooth_number,
            "surface_ids": entry.surface_ids,
            "area_of_oral_cavity": entry.area_of_oral_cavity,
            "note_type": entry.note_type,
        })
    
    return schemas.NoteHistoryListResponse(
        items=items,
        total=len(items)
    )

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
    
    # Trigger patient summary generation (async via Cloud Tasks)
    from app.services.task_queue import enqueue_summary_generation
    await enqueue_summary_generation(
        patient_id=note.patient_id,
        note_id=db_note.id,
        office_id=tenant_id
    )
    
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
