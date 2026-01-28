from datetime import timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import secrets

from app.db.session import get_db
from app.core import security
from app.core.config import settings
from app.models import User, Office, ApiKey
from app.schemas import auth as schemas
from app.api import deps

router = APIRouter()

@router.post("/register", response_model=schemas.Token)
async def register(
    data: schemas.RegisterRequest, 
    db: AsyncSession = Depends(get_db)
) -> Any:
    # 1. Check if user exists
    result = await db.execute(select(User).filter(User.email == data.user.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # 2. Create Office
    office = Office(
        name=data.office.name,
        address=data.office.address
    )
    db.add(office)
    await db.commit() # Commit to generate ID
    await db.refresh(office)
    
    # 3. Create User (Admin)
    user = User(
        email=data.user.email,
        hashed_password=security.get_password_hash(data.user.password),
        full_name=data.user.full_name,
        role="ADMIN",
        office_id=office.id
    )
    db.add(user)
    
    # 4. Create Default API Key? (Optional, let's skip automatic key for now, they can generate one)
    
    await db.commit()
    
    # 5. Generate Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login", response_model=schemas.Token)
async def login(
    login_data: schemas.UserLogin, 
    db: AsyncSession = Depends(get_db)
) -> Any:
    # 1. Fetch User
    result = await db.execute(select(User).filter(User.email == login_data.email))
    user = result.scalars().first()
    
    # 2. Validate
    if not user or not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # 3. Generate Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/keys", response_model=schemas.ApiKeyResponse)
async def create_api_key(
    key_data: schemas.ApiKeyCreate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # 1. Generate Key
    # Format: sk_live_<24 random hex chars>
    raw_key = f"sk_live_{secrets.token_hex(24)}"
    key_hash = security.get_api_key_hash(raw_key)
    prefix = raw_key[:12] + "..." # Store prefix for display
    
    # 2. Store Hash
    api_key = ApiKey(
        key_hash=key_hash,
        prefix=prefix,
        name=key_data.name,
        office_id=current_user.office_id,
        is_active=True
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    # 3. Return (Inject raw key ONE TIME)
    # We construct response manually or patch object
    response = schemas.ApiKeyResponse.model_validate(api_key)
    response.key = raw_key # Inject cleartext key
    return response

@router.get("/keys", response_model=List[schemas.ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(ApiKey).filter(ApiKey.office_id == current_user.office_id))
    keys = result.scalars().all()
    return keys
