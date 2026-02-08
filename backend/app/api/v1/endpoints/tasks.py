from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models import Task
from app.schemas import task as schemas
from app.api.deps import get_current_tenant_id

router = APIRouter()

@router.post("", response_model=schemas.TaskResponse)
async def create_task(
    task: schemas.TaskCreate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    db_task = Task(
        patient_id=task.patient_id,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        generated_by=task.generated_by,
        assignee_type=task.assignee_type,
        office_id=tenant_id
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("", response_model=List[schemas.TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    assignee_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """List all tasks for the office with optional status/assignee_type filter and pagination."""
    query = select(Task).filter(Task.office_id == tenant_id)
    
    if status:
        query = query.filter(Task.status == status)
    if assignee_type:
        query = query.filter(Task.assignee_type == assignee_type)
    
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/patient/{patient_id}", response_model=List[schemas.TaskResponse])
async def read_patient_tasks(
    patient_id: UUID, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(Task).filter(Task.patient_id == patient_id, Task.office_id == tenant_id))
    return result.scalars().all()

@router.get("/{task_id}", response_model=schemas.TaskResponse)
async def read_task(
    task_id: UUID, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(Task).filter(Task.id == task_id, Task.office_id == tenant_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
@router.patch("/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: UUID, 
    task_update: schemas.TaskUpdate, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(Task).filter(Task.id == task_id, Task.office_id == tenant_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.description:
        db_task.description = task_update.description
    if task_update.status:
        db_task.status = task_update.status
    if task_update.priority:
        db_task.priority = task_update.priority
    if task_update.due_date:
        db_task.due_date = task_update.due_date
    if task_update.assignee_type:
        db_task.assignee_type = task_update.assignee_type

    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID, 
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    result = await db.execute(select(Task).filter(Task.id == task_id, Task.office_id == tenant_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(db_task)
    await db.commit()
