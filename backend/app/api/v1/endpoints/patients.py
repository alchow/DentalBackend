from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models import Patient
from app.schemas import patient as schemas
from app.core.security import encrypt_data, decrypt_data, get_blind_index, parse_ssn_input, mask_ssn
from app.api.deps import get_current_tenant_id
from sqlalchemy import or_

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
    
    # Handle SSN
    ssn_encrypted = None
    ssn_hash = None
    last_4_ssn_hash = None
    if patient.ssn:
        full_ssn, last_4 = parse_ssn_input(patient.ssn)
        if full_ssn:
            ssn_encrypted = encrypt_data(full_ssn)
            ssn_hash = get_blind_index(full_ssn)
        if last_4:
            last_4_ssn_hash = get_blind_index(last_4)
    
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
        is_active=True,
        ssn_encrypted=ssn_encrypted,
        ssn_hash=ssn_hash,
        last_4_ssn_hash=last_4_ssn_hash
    )
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    
    # Decrypt for response
    db_patient.first_name = patient.first_name
    db_patient.last_name = patient.last_name
    
    # Add masked SSN to response
    if last_4_ssn_hash:
        _, last_4 = parse_ssn_input(patient.ssn)
        db_patient.ssn_last_4 = mask_ssn(last_4)
    
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
    
    # Handle SSN update
    if patient_update.ssn is not None:
        if patient_update.ssn == "":  # Clear SSN
            db_patient.ssn_encrypted = None
            db_patient.ssn_hash = None
            db_patient.last_4_ssn_hash = None
        else:
            full_ssn, last_4 = parse_ssn_input(patient_update.ssn)
            if full_ssn:
                db_patient.ssn_encrypted = encrypt_data(full_ssn)
                db_patient.ssn_hash = get_blind_index(full_ssn)
            else:
                db_patient.ssn_encrypted = None
                db_patient.ssn_hash = None
            if last_4:
                db_patient.last_4_ssn_hash = get_blind_index(last_4)
            else:
                db_patient.last_4_ssn_hash = None

    await db.commit()
    await db.refresh(db_patient)

    # Decrypt for response
    db_patient.first_name = decrypt_data(db_patient.first_name)
    db_patient.last_name = decrypt_data(db_patient.last_name)
    
    # Add masked SSN
    if db_patient.ssn_encrypted:
        full_ssn = decrypt_data(db_patient.ssn_encrypted)
        db_patient.ssn_last_4 = mask_ssn(full_ssn[-4:])
    elif db_patient.last_4_ssn_hash:
        # Can't recover last-4 from hash, but we know it exists
        db_patient.ssn_last_4 = "***-**-****"  # Indicate SSN exists but masked

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


@router.get("/search/ssn", response_model=List[schemas.PatientResponse])
async def search_by_ssn(
    ssn: str = Query(..., description="Full SSN (XXX-XX-XXXX) or last 4 digits"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Search patients by full SSN or last 4 digits."""
    full_ssn, last_4 = parse_ssn_input(ssn)
    
    if not full_ssn and not last_4:
        raise HTTPException(status_code=400, detail="Invalid SSN format. Use XXX-XX-XXXX or last 4 digits.")
    
    # Build query based on what was provided
    query = select(Patient).filter(Patient.office_id == tenant_id, Patient.is_active.is_(True))
    
    if full_ssn:
        # Search by full SSN hash (exact match)
        query = query.filter(Patient.ssn_hash == get_blind_index(full_ssn))
    else:
        # Search by last 4 hash
        query = query.filter(Patient.last_4_ssn_hash == get_blind_index(last_4))
    
    result = await db.execute(query)
    patients = result.scalars().all()
    
    # Decrypt and add masked SSN
    for p in patients:
        p.first_name = decrypt_data(p.first_name)
        p.last_name = decrypt_data(p.last_name)
        if p.ssn_encrypted:
            decrypted = decrypt_data(p.ssn_encrypted)
            p.ssn_last_4 = mask_ssn(decrypted[-4:])
        elif p.last_4_ssn_hash:
            p.ssn_last_4 = "***-**-****"
    
    return patients


@router.post("/check-duplicate", response_model=schemas.DuplicateCheckResponse)
async def check_duplicate(
    data: schemas.DuplicateCheckRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Check for potential duplicate patients before creation.
    Returns matches ordered by confidence: HIGH → MEDIUM → LOW.
    """
    potential_duplicates = []
    seen_ids = set()  # Avoid duplicate entries in response
    
    # Compute hashes for matching
    last_name_hash = get_blind_index(data.last_name)
    first_name_hash = get_blind_index(data.first_name) if data.first_name else None
    phone_hash = get_blind_index(data.phone) if data.phone else None
    
    ssn_hash = None
    last_4_ssn_hash = None
    if data.ssn:
        full_ssn, last_4 = parse_ssn_input(data.ssn)
        if full_ssn:
            ssn_hash = get_blind_index(full_ssn)
        if last_4:
            last_4_ssn_hash = get_blind_index(last_4)
    
    # BASE FILTER: active patients in same office
    base_filter = [Patient.office_id == tenant_id, Patient.is_active.is_(True)]
    
    # TIER 1: HIGH confidence - Full SSN exact match
    if ssn_hash:
        result = await db.execute(
            select(Patient).filter(*base_filter, Patient.ssn_hash == ssn_hash)
        )
        for p in result.scalars().all():
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                potential_duplicates.append(schemas.PotentialDuplicate(
                    id=p.id,
                    first_name=decrypt_data(p.first_name),
                    last_name=decrypt_data(p.last_name),
                    dob=p.dob,
                    match_confidence="HIGH",
                    match_reason="SSN exact match"
                ))
    
    # TIER 2: MEDIUM confidence - SSN last-4 + DOB + Last Name
    if last_4_ssn_hash:
        result = await db.execute(
            select(Patient).filter(
                *base_filter,
                Patient.last_4_ssn_hash == last_4_ssn_hash,
                Patient.dob == data.dob,
                Patient.last_name_hash == last_name_hash
            )
        )
        for p in result.scalars().all():
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                potential_duplicates.append(schemas.PotentialDuplicate(
                    id=p.id,
                    first_name=decrypt_data(p.first_name),
                    last_name=decrypt_data(p.last_name),
                    dob=p.dob,
                    match_confidence="MEDIUM",
                    match_reason="SSN last-4 + DOB + Last Name"
                ))
    
    # TIER 2B: MEDIUM confidence - DOB + First Name + Last Name (no SSN needed)
    if first_name_hash:
        result = await db.execute(
            select(Patient).filter(
                *base_filter,
                Patient.dob == data.dob,
                Patient.first_name_hash == first_name_hash,
                Patient.last_name_hash == last_name_hash
            )
        )
        for p in result.scalars().all():
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                potential_duplicates.append(schemas.PotentialDuplicate(
                    id=p.id,
                    first_name=decrypt_data(p.first_name),
                    last_name=decrypt_data(p.last_name),
                    dob=p.dob,
                    match_confidence="MEDIUM",
                    match_reason="DOB + First Name + Last Name"
                ))
    
    # TIER 3: LOW confidence - Phone + Last Name
    if phone_hash:
        result = await db.execute(
            select(Patient).filter(
                *base_filter,
                Patient.phone_hash == phone_hash,
                Patient.last_name_hash == last_name_hash
            )
        )
        for p in result.scalars().all():
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                potential_duplicates.append(schemas.PotentialDuplicate(
                    id=p.id,
                    first_name=decrypt_data(p.first_name),
                    last_name=decrypt_data(p.last_name),
                    dob=p.dob,
                    match_confidence="LOW",
                    match_reason="Phone + Last Name"
                ))
    
    # TIER 3B: LOW confidence - DOB + Last Name only
    result = await db.execute(
        select(Patient).filter(
            *base_filter,
            Patient.dob == data.dob,
            Patient.last_name_hash == last_name_hash
        )
    )
    for p in result.scalars().all():
        if p.id not in seen_ids:
            seen_ids.add(p.id)
            potential_duplicates.append(schemas.PotentialDuplicate(
                id=p.id,
                first_name=decrypt_data(p.first_name),
                last_name=decrypt_data(p.last_name),
                dob=p.dob,
                match_confidence="LOW",
                match_reason="DOB + Last Name"
            ))
    
    return schemas.DuplicateCheckResponse(potential_duplicates=potential_duplicates)
