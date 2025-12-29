from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models import Visit
from app.schemas import visit_note as schemas

router = APIRouter()

@router.post("/", response_model=schemas.VisitResponse)
async def create_visit(visit: schemas.VisitCreate, db: AsyncSession = Depends(get_db)):
    db_visit = Visit(**visit.model_dump())
    db.add(db_visit)
    await db.commit()
    await db.refresh(db_visit)
    return db_visit

@router.get("/patient/{patient_id}", response_model=List[schemas.VisitResponse])
async def read_patient_visits(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visit).filter(Visit.patient_id == patient_id))
    return result.scalars().all()

@router.get("/{visit_id}", response_model=schemas.VisitResponse)
async def read_visit(visit_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Visit).filter(Visit.id == visit_id))
    visit = result.scalars().first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit
