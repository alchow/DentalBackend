from typing import Generator, Optional, Union
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models import User, ApiKey
from app.models.office import Office

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)
# We accept X-Office-Key provided mechanism
api_key_header = APIKeyHeader(name="X-Office-Key", auto_error=False)

async def get_current_tenant_id(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2),
    x_office_key: str = Security(api_key_header)
) -> str:
    """
    Returns the office_id (UUID) for the current request.
    Prioritizes X-Office-Key (System) -> JWT (User).
    """
    # 1. Check API Key first (System/Office Access)
    if x_office_key:
        api_key_hash = security.get_api_key_hash(x_office_key)
        # Verify Key in DB
        result = await db.execute(select(ApiKey).filter(ApiKey.key_hash == api_key_hash))
        api_key_obj = result.scalars().first()
        
        if api_key_obj and api_key_obj.is_active:
            return api_key_obj.office_id
        # If key provided but invalid, we might want to fail fast, but let's fall through
        # implementation detail: if key is wrong, request is unauthorized regardless of JWT?
        # For now, if key is wrong, we return 401.
        raise HTTPException(status_code=401, detail="Invalid Office Key")
    
    # 2. Check JWT (User Access)
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=403, detail="Could not validate credentials")
            
            # Fetch User to get Office ID
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            if not user or not user.is_active:
                 raise HTTPException(status_code=403, detail="User not found or inactive")
            
            return user.office_id
            
        except (JWTError, ValidationError):
             raise HTTPException(status_code=403, detail="Could not validate credentials")

    # 3. Fail if neither
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide Bearer Token or X-Office-Key.",
    )

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    Extracts User from JWT. Used for endpoints requiring specific user role (Author).
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
             raise HTTPException(status_code=403, detail="Could not validate credentials")
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
