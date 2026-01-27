from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class ContactInfo(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    dob: date
    contact_info: Optional[ContactInfo] = None
    medical_history: Optional[dict] = None # Allergies, Meds

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[date] = None
    contact_info: Optional[ContactInfo] = None
    medical_history: Optional[dict] = None

class PatientResponse(PatientBase):
    id: UUID
    last_name_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
