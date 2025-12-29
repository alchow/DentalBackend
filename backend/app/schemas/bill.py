from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum
from decimal import Decimal

class BillStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    INSURANCE_CLAIMED = "INSURANCE_CLAIMED"

class CdtCodeBase(BaseModel):
    code: str
    description: str
    category: Optional[str] = None

class BillBase(BaseModel):
    patient_id: UUID
    visit_id: UUID
    amount: Decimal
    status: BillStatus = BillStatus.PENDING

class BillCreate(BillBase):
    codes: List[str] # List of CDT Codes

class BillUpdate(BaseModel):
    amount: Optional[Decimal] = None
    status: Optional[BillStatus] = None
    codes: Optional[List[str]] = None

class BillResponse(BillBase):
    id: UUID
    codes: List[CdtCodeBase]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
