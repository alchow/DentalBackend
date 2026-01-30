from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models import Patient
from app.schemas import patient as schemas
from app.core.security import encrypt_data, decrypt_data, get_blind_index
from app.api.deps import get_current_tenant_id

router = APIRouter()

@router.post("", response_model=schemas.PatientResponse)
async def create_patient(
    patient: schemas.PatientCreate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    # Encrypt sensitive fields
    encrypted_first = encrypt_data(patient.first_name)
    encrypted_last = encrypt_data(patient.last_name)
    last_name_hash = get_blind_index(patient.last_name)
    first_name_hash = get_blind_index(patient.first_name)
    
    # Extract phone for hash if provided
    phone_hash = None
    if patient.contact_info and patient.contact_info.phone:
        phone_hash = get_blind_index(patient.contact_info.phone)
    
    db_patient = Patient(
        first_name=encrypted_first,
        last_name=encrypted_last,
        last_name_hash=last_name_hash,
        first_name_hash=first_name_hash,
        phone_hash=phone_hash,
        dob=patient.dob,
        contact_info=patient.contact_info.model_dump() if patient.contact_info else None,
        medical_history=patient.medical_history,
        office_id=tenant_id,
        is_active=True
    )
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    
    # Decrypt for response
    db_patient.first_name = patient.first_name
    db_patient.last_name = patient.last_name
    
    return db_patient


@router.get("", response_model=List[schemas.PatientResponse])
async def list_patients(
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List all active patients for the office with pagination."""
    result = await db.execute(
        select(Patient)
        .filter(Patient.office_id == tenant_id, Patient.is_active == True)
        .order_by(Patient.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    patients = result.scalars().all()
    
    # Decrypt all patient names
    for p in patients:
        p.first_name = decrypt_data(p.first_name)
        p.last_name = decrypt_data(p.last_name)
    
    return patients


@router.put("/{patient_id}", response_model=schemas.PatientResponse)
@router.patch("/{patient_id}", response_model=schemas.PatientResponse)
async def update_patient(
    patient_id: UUID, 
    patient_update: schemas.PatientUpdate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(Patient).filter(Patient.id == patient_id, Patient.office_id == tenant_id))
    db_patient = result.scalars().first()
    if not db_patient or not db_patient.is_active:
        raise HTTPException(status_code=404, detail="Patient not found")

    if patient_update.first_name:
        db_patient.first_name = encrypt_data(patient_update.first_name)
        db_patient.first_name_hash = get_blind_index(patient_update.first_name)
    if patient_update.last_name:
        db_patient.last_name = encrypt_data(patient_update.last_name)
        db_patient.last_name_hash = get_blind_index(patient_update.last_name)
    if patient_update.dob:
        db_patient.dob = patient_update.dob
    if patient_update.contact_info:
        db_patient.contact_info = patient_update.contact_info.model_dump()
        # Update phone hash if phone changed
        if patient_update.contact_info.phone:
            db_patient.phone_hash = get_blind_index(patient_update.contact_info.phone)
    if patient_update.medical_history is not None:
        db_patient.medical_history = patient_update.medical_history

    await db.commit()
    await db.refresh(db_patient)

    # Decrypt for response
    db_patient.first_name = decrypt_data(db_patient.first_name)
    db_patient.last_name = decrypt_data(db_patient.last_name)

    return db_patient

@router.get("/{patient_id}", response_model=schemas.PatientResponse)
async def read_patient(
    patient_id: UUID, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(Patient).filter(Patient.id == patient_id, Patient.office_id == tenant_id))
    patient = result.scalars().first()
    if not patient or not patient.is_active:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Decrypt
    patient.first_name = decrypt_data(patient.first_name)
    patient.last_name = decrypt_data(patient.last_name)
    return patient

@router.delete("/{patient_id}", status_code=204)
async def delete_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Soft delete patient"""
    result = await db.execute(select(Patient).filter(Patient.id == patient_id, Patient.office_id == tenant_id))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    patient.is_active = False
    await db.commit()
    return

@router.get("/search/query", response_model=List[schemas.PatientResponse])
async def search_patients(
    last_name: Optional[str] = Query(None, description="Search by last name"),
    first_name: Optional[str] = Query(None, description="Search by first name"),
    phone: Optional[str] = Query(None, description="Search by phone number"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Search patients by last name, first name, and/or phone. All params are AND'd together."""
    if not last_name and not first_name and not phone:
        raise HTTPException(status_code=400, detail="At least one search parameter required")
    
    # Build query with filters
    query = select(Patient).filter(Patient.office_id == tenant_id, Patient.is_active.is_(True))
    
    if last_name:
        query = query.filter(Patient.last_name_hash == get_blind_index(last_name))
    if first_name:
        query = query.filter(Patient.first_name_hash == get_blind_index(first_name))
    if phone:
        query = query.filter(Patient.phone_hash == get_blind_index(phone))
    
    result = await db.execute(query)
    patients = result.scalars().all()
    
    # Decrypt all
    for p in patients:
        p.first_name = decrypt_data(p.first_name)
        p.last_name = decrypt_data(p.last_name)
        
    return patients
