from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

# --- Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# --- User ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    
class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    office_id: UUID
    is_active: bool
    role: str
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Office ---
class OfficeBase(BaseModel):
    name: str
    address: Optional[str] = None

class OfficeCreate(OfficeBase):
    pass

class OfficeResponse(OfficeBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Registration ---
class RegisterRequest(BaseModel):
    office: OfficeCreate
    user: UserCreate

# --- API Keys ---
class ApiKeyCreate(BaseModel):
    name: Optional[str] = None

class ApiKeyResponse(BaseModel):
    id: UUID
    prefix: str
    name: Optional[str]
    created_at: datetime
    key: Optional[str] = None # Only returned on creation
    
    class Config:
        from_attributes = True

# --- Password Reset ---
class AdminPasswordResetRequest(BaseModel):
    """Admin requests a reset link for a user"""
    user_email: EmailStr

class AdminPasswordResetResponse(BaseModel):
    """Returns reset link for admin to share with user"""
    reset_token: str
    reset_link: str
    expires_in_minutes: int = 60
    user_email: str

class PasswordResetRequest(BaseModel):
    """User resets their password using the token"""
    token: str
    new_password: str

class PasswordResetResponse(BaseModel):
    success: bool
    message: str
