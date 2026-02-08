from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.db.session import get_db
from app.models import Visit
from app.models.visit import VisitStatus
from app.schemas import visit_note as schemas
from app.api.deps import get_current_tenant_id

router = APIRouter()

@router.post("", response_model=schemas.VisitResponse)
async def create_visit(
    visit: schemas.VisitCreate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    db_visit = Visit(
        **visit.model_dump(),
        office_id=tenant_id
    )
    db.add(db_visit)
    await db.commit()
    await db.refresh(db_visit)
    return db_visit

@router.get("/schedule", response_model=List[schemas.VisitResponse])
async def get_schedule(
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Fetch all visits for a specific date (schedule view)."""
    result = await db.execute(
        select(Visit).filter(
            Visit.office_id == tenant_id,
            func.date(Visit.visit_date) == date,
            Visit.status != VisitStatus.DELETED
        )
    )
    return result.scalars().all()

@router.get("/patient/{patient_id}", response_model=List[schemas.VisitResponse])
async def read_patient_visits(
    patient_id: UUID, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(
        select(Visit).filter(
            Visit.patient_id == patient_id, 
            Visit.office_id == tenant_id,
            Visit.status != VisitStatus.DELETED
        )
    )
    return result.scalars().all()

@router.get("/{visit_id}", response_model=schemas.VisitResponse)
async def read_visit(
    visit_id: UUID, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(
        select(Visit).filter(
            Visit.id == visit_id, 
            Visit.office_id == tenant_id,
            Visit.status != VisitStatus.DELETED
        )
    )
    visit = result.scalars().first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.patch("/{visit_id}", response_model=schemas.VisitResponse)
async def update_visit(
    visit_id: UUID,
    visit_update: schemas.VisitUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Update visit status, reason, date, or duration."""
    result = await db.execute(
        select(Visit).filter(
            Visit.id == visit_id, 
            Visit.office_id == tenant_id,
            Visit.status != VisitStatus.DELETED
        )
    )
    db_visit = result.scalars().first()
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    if visit_update.visit_date is not None:
        db_visit.visit_date = visit_update.visit_date
    if visit_update.reason is not None:
        db_visit.reason = visit_update.reason
    if visit_update.status is not None:
        db_visit.status = visit_update.status
    if visit_update.duration_minutes is not None:
        db_visit.duration_minutes = visit_update.duration_minutes

    await db.commit()
    await db.refresh(db_visit)
    return db_visit

@router.delete("/{visit_id}", status_code=204)
async def delete_visit(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Soft delete a visit (sets status to DELETED)."""
    result = await db.execute(
        select(Visit).filter(
            Visit.id == visit_id, 
            Visit.office_id == tenant_id,
            Visit.status != VisitStatus.DELETED
        )
    )
    db_visit = result.scalars().first()
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    db_visit.status = VisitStatus.DELETED
    await db.commit()

