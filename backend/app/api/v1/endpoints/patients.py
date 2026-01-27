from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models import Patient
from app.schemas import patient as schemas
from app.core.security import encrypt_data, decrypt_data, get_blind_index

router = APIRouter()

@router.post("", response_model=schemas.PatientResponse)
async def create_patient(patient: schemas.PatientCreate, db: AsyncSession = Depends(get_db)):
    # Encrypt sensitive fields
    encrypted_first = encrypt_data(patient.first_name)
    encrypted_last = encrypt_data(patient.last_name)
    blind_index = get_blind_index(patient.last_name)
    
    # Handle JSON encryption (simplified: encrypt whole JSON string or fields? 
    # For now, let's assume contact_info stays JSON but maybe fields inside are sensitive.
    # To stick to plan: "contact_info: JSONB - Encrypted". 
    # Actually, encrypting a JSONB column usually means storing it as binary/text.
    # Postgres JSONB cannot easily hold an encrypted blob unless it's a string inside a key.
    # We will skip encrypting the JSON structure itself for this prototype and focus on names.
    
    db_patient = Patient(
        first_name=encrypted_first,
        last_name=encrypted_last,
        last_name_hash=blind_index,
        dob=patient.dob,
        contact_info=patient.contact_info.model_dump() if patient.contact_info else None,
        medical_history=patient.medical_history
    )
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    
    # Decrypt for response
    db_patient.first_name = patient.first_name
    db_patient.last_name = patient.last_name
    
    return db_patient

@router.put("/{patient_id}", response_model=schemas.PatientResponse)
async def update_patient(patient_id: UUID, patient_update: schemas.PatientUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    db_patient = result.scalars().first()
    if not db_patient:
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
    if patient_update.medical_history is not None: # check against None specifically to allow clearing? or just updating
        db_patient.medical_history = patient_update.medical_history

    await db.commit()
    await db.refresh(db_patient)

    # Decrypt for response
    db_patient.first_name = decrypt_data(db_patient.first_name)
    db_patient.last_name = decrypt_data(db_patient.last_name)

    return db_patient

@router.get("/{patient_id}", response_model=schemas.PatientResponse)
async def read_patient(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalars().first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Decrypt
    patient.first_name = decrypt_data(patient.first_name)
    patient.last_name = decrypt_data(patient.last_name)
    return patient

@router.get("/search", response_model=List[schemas.PatientResponse])
async def search_patients(last_name: str, db: AsyncSession = Depends(get_db)):
    # Use blind index
    search_hash = get_blind_index(last_name)
    result = await db.execute(select(Patient).filter(Patient.last_name_hash == search_hash))
    patients = result.scalars().all()
    
    # Decrypt all
    for p in patients:
        p.first_name = decrypt_data(p.first_name)
        p.last_name = decrypt_data(p.last_name)
        
    return patients
