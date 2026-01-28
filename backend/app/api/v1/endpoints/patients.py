from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
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
    blind_index = get_blind_index(patient.last_name)
    
    db_patient = Patient(
        first_name=encrypted_first,
        last_name=encrypted_last,
        last_name_hash=blind_index,
        dob=patient.dob,
        contact_info=patient.contact_info.model_dump() if patient.contact_info else None,
        medical_history=patient.medical_history,
        office_id=tenant_id, # Assign Tenant
        is_active=True
    )
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    
    # Decrypt for response
    db_patient.first_name = patient.first_name
    db_patient.last_name = patient.last_name
    
    return db_patient

@router.put("/{patient_id}", response_model=schemas.PatientResponse)
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
    if patient_update.last_name:
        db_patient.last_name = encrypt_data(patient_update.last_name)
        db_patient.last_name_hash = get_blind_index(patient_update.last_name)
    if patient_update.dob:
        db_patient.dob = patient_update.dob
    if patient_update.contact_info:
        db_patient.contact_info = patient_update.contact_info.model_dump()
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

@router.get("/search/query", response_model=List[schemas.PatientResponse]) # Changed path to avoid conflict if needed, or query param
async def search_patients(
    last_name: str, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    # Use blind index
    search_hash = get_blind_index(last_name)
    result = await db.execute(
        select(Patient)
        .filter(Patient.last_name_hash == search_hash, Patient.office_id == tenant_id, Patient.is_active.is_(True))
    )
    patients = result.scalars().all()
    
    # Decrypt all
    for p in patients:
        p.first_name = decrypt_data(p.first_name)
        p.last_name = decrypt_data(p.last_name)
        
    return patients
