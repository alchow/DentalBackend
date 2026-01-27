from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models import Task
from app.schemas import task as schemas

router = APIRouter()

@router.post("", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(
        patient_id=task.patient_id,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        generated_by=task.generated_by
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("/patient/{patient_id}", response_model=List[schemas.TaskResponse])
async def read_patient_tasks(patient_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.patient_id == patient_id))
    return result.scalars().all()

@router.put("/{task_id}", response_model=schemas.TaskResponse)
async def update_task(task_id: UUID, task_update: schemas.TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
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

    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(db_task)
    await db.commit()
