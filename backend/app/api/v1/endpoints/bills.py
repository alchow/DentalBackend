from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models import Bill, CdtCode
from app.schemas import bill as schemas

router = APIRouter()

@router.post("", response_model=schemas.BillResponse)
async def create_bill(bill: schemas.BillCreate, db: AsyncSession = Depends(get_db)):
    # 1. Handle Codes
    # Find or create codes
    code_objs = []
    for code_str in bill.codes:
        result = await db.execute(select(CdtCode).filter(CdtCode.code == code_str))
        cdt_code = result.scalars().first()
        if not cdt_code:
            # Create if not exists (Prototype helper)
            cdt_code = CdtCode(code=code_str, description="Auto-created", category="General")
            db.add(cdt_code)
            # Need to flush to get ID availability for relationship? 
            # In async session, objects are tracked.
        code_objs.append(cdt_code)
    
    # 2. Create Bill
    db_bill = Bill(
        patient_id=bill.patient_id,
        visit_id=bill.visit_id,
        amount=bill.amount,
        status=bill.status,
        codes=code_objs # SQLA handles M2M insert
    )
    db.add(db_bill)
    db.add(db_bill)
    await db.commit()
    
    # Reload with eager load for response
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Bill).options(selectinload(Bill.codes)).filter(Bill.id == db_bill.id)
    )
    return result.scalars().first()

@router.get("/patient/{patient_id}", response_model=List[schemas.BillResponse])
async def read_patient_bills(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    # Need joinedload for codes?
    # Default lazy load might fail in async if session closed, but FastAPI dependency keeps it open? 
    # Use select(Bill).options(selectinload(Bill.codes)) is safer.
    from sqlalchemy.orm import selectinload
    result = await db.execute(select(Bill).filter(Bill.patient_id == patient_id).options(selectinload(Bill.codes)))
    return result.scalars().all()
