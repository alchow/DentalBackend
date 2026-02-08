"""Backfill API endpoints for historical data import.

These endpoints allow creating records with custom created_at timestamps.
Requires API key authentication only (Bearer tokens are rejected).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import require_api_key_only
from app.models.note import Note
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.bill import Bill, CdtCode, bill_codes_association
from app.schemas import backfill as schemas
from app.core.security import encrypt_data, get_blind_index as compute_blind_index
from sqlalchemy.future import select

router = APIRouter()


@router.post("/notes", response_model=schemas.BackfillResponse, status_code=201)
async def backfill_note(
    data: schemas.NoteBackfillCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(require_api_key_only)
):
    """
    Create a clinical note with a custom created_at timestamp.
    
    - **Requires API key authentication** (X-Office-Key header)
    - created_at must be a date in the past
    - Sets is_backfilled=True for audit trail
    """
    encrypted_content = encrypt_data(data.content)
    
    db_note = Note(
        patient_id=data.patient_id,
        visit_id=data.visit_id,
        content=encrypted_content,
        area_of_oral_cavity=data.area_of_oral_cavity,
        tooth_number=data.tooth_number,
        surface_ids=data.surface_ids,
        note_type=data.note_type,
        author_id=data.author_id,
        office_id=tenant_id,
        created_at=data.created_at,
        is_backfilled=True
    )
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    
    # Index for search (optional, but consistent with normal create)
    try:
        from app.services.search_service import SearchService
        search_service = SearchService(db)
        await search_service.index_note(db_note.id, data.content)
    except Exception:
        pass  # Don't fail backfill if search indexing fails
    
    return db_note


@router.post("/patients", response_model=schemas.BackfillResponse, status_code=201)
async def backfill_patient(
    data: schemas.PatientBackfillCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(require_api_key_only)
):
    """
    Create a patient with a custom created_at timestamp.
    
    - **Requires API key authentication** (X-Office-Key header)
    - created_at must be a date in the past
    - Sets is_backfilled=True for audit trail
    """
    # Encrypt sensitive fields
    encrypted_first_name = encrypt_data(data.first_name)
    encrypted_last_name = encrypt_data(data.last_name)
    last_name_hash = compute_blind_index(data.last_name.lower())
    first_name_hash = compute_blind_index(data.first_name.lower())
    
    # Handle contact info
    encrypted_contact = None
    phone_hash = None
    if data.contact_info:
        contact_dict = data.contact_info.model_dump()
        encrypted_contact = encrypt_data(str(contact_dict))
        if data.contact_info.phone:
            # Normalize phone for hashing
            phone_digits = ''.join(filter(str.isdigit, data.contact_info.phone))
            phone_hash = compute_blind_index(phone_digits)
    
    db_patient = Patient(
        first_name=encrypted_first_name,
        last_name=encrypted_last_name,
        last_name_hash=last_name_hash,
        first_name_hash=first_name_hash,
        phone_hash=phone_hash,
        dob=data.dob,
        contact_info=encrypted_contact,
        medical_history=data.medical_history,
        office_id=tenant_id,
        created_at=data.created_at,
        is_backfilled=True
    )
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    
    return db_patient


@router.post("/visits", response_model=schemas.BackfillResponse, status_code=201)
async def backfill_visit(
    data: schemas.VisitBackfillCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(require_api_key_only)
):
    """
    Create a visit with a custom created_at timestamp.
    
    - **Requires API key authentication** (X-Office-Key header)
    - created_at must be a date in the past
    - Sets is_backfilled=True for audit trail
    """
    from app.models.visit import VisitStatus as ModelVisitStatus
    
    db_visit = Visit(
        patient_id=data.patient_id,
        visit_date=data.visit_date,
        reason=data.reason,
        status=ModelVisitStatus(data.status.value) if data.status else ModelVisitStatus.SCHEDULED,
        duration_minutes=data.duration_minutes,
        office_id=tenant_id,
        created_at=data.created_at,
        is_backfilled=True
    )
    db.add(db_visit)
    await db.commit()
    await db.refresh(db_visit)
    
    return db_visit


@router.post("/bills", response_model=schemas.BackfillResponse, status_code=201)
async def backfill_bill(
    data: schemas.BillBackfillCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(require_api_key_only)
):
    """
    Create a bill with a custom created_at timestamp.
    
    - **Requires API key authentication** (X-Office-Key header)
    - created_at must be a date in the past
    - Sets is_backfilled=True for audit trail
    """
    from app.models.bill import BillStatus as ModelBillStatus
    
    db_bill = Bill(
        patient_id=data.patient_id,
        visit_id=data.visit_id,
        amount=data.amount,
        status=ModelBillStatus(data.status.value) if data.status else ModelBillStatus.PENDING,
        office_id=tenant_id,
        created_at=data.created_at,
        is_backfilled=True
    )
    db.add(db_bill)
    await db.commit()
    
    # Link CDT codes if provided (use raw insert to avoid async lazy loading issue)
    if data.codes:
        from sqlalchemy import insert
        for code_str in data.codes:
            result = await db.execute(select(CdtCode).filter(CdtCode.code == code_str))
            cdt_code = result.scalars().first()
            if cdt_code:
                await db.execute(
                    insert(bill_codes_association).values(
                        bill_id=db_bill.id, 
                        code_id=cdt_code.code
                    )
                )
        await db.commit()
    
    await db.refresh(db_bill)
    
    return db_bill
