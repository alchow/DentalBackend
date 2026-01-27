from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID

class TaskBase(BaseModel):
    description: str
    status: str = "PENDING"
    priority: str = "NORMAL"
    due_date: Optional[date] = None
    patient_id: UUID
    generated_by: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None

class TaskResponse(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
