from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
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
    ssn: Optional[str] = None  # Accepts full (XXX-XX-XXXX) or last-4 (XXXX)
    
    @field_validator('ssn')
    @classmethod
    def validate_ssn(cls, v):
        if v is None:
            return v
        import re
        digits = re.sub(r'[\s\-]', '', v)
        if len(digits) not in (4, 9):
            raise ValueError('SSN must be 4 digits (last-4) or 9 digits (full)')
        if not digits.isdigit():
            raise ValueError('SSN must contain only digits')
        return v

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[date] = None
    contact_info: Optional[ContactInfo] = None
    medical_history: Optional[dict] = None
    ssn: Optional[str] = None  # Can add, change, or clear SSN
    
    @field_validator('ssn')
    @classmethod
    def validate_ssn(cls, v):
        if v is None or v == "":  # Empty string clears SSN
            return v
        import re
        digits = re.sub(r'[\s\-]', '', v)
        if len(digits) not in (4, 9):
            raise ValueError('SSN must be 4 digits (last-4) or 9 digits (full)')
        if not digits.isdigit():
            raise ValueError('SSN must contain only digits')
        return v

class PatientResponse(PatientBase):
    id: UUID
    last_name_hash: str
    created_at: datetime
    updated_at: datetime
    ssn_last_4: Optional[str] = None  # Masked display: "***-**-1234"

    class Config:
        from_attributes = True


# --- Duplicate Detection Schemas ---

class DuplicateCheckRequest(BaseModel):
    """Request to check for potential duplicate patients."""
    first_name: Optional[str] = None
    last_name: str
    dob: date
    ssn: Optional[str] = None  # Full or last-4
    phone: Optional[str] = None

class PotentialDuplicate(BaseModel):
    """A potential duplicate patient match."""
    id: UUID
    first_name: str
    last_name: str
    dob: date
    match_confidence: str  # "HIGH", "MEDIUM", "LOW"
    match_reason: str  # "SSN exact match", "SSN last-4 + DOB + Name", etc.

class DuplicateCheckResponse(BaseModel):
    """Response with list of potential duplicates."""
    potential_duplicates: List[PotentialDuplicate]

