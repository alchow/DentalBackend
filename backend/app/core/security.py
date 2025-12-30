from cryptography.fernet import Fernet
from passlib.context import CryptContext
import hashlib
import os

# Generate a key for development - in Prod this comes from KMS
# For now we generate a random key if not present in env
# A real implementation would fetch this from GCP KMS
DEV_KEY = os.getenv("ENCRYPTION_KEY", "mNDwH60iN1a1xkB6-oJR4lHJ5-dxc-mQII86XXdQC90=")
fernet = Fernet(DEV_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encrypt_data(data: str) -> str:
    if not data: return data
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    if not data: return data
    return fernet.decrypt(data.encode()).decode()

def get_blind_index(data: str) -> str:
    """Deterministic hash for searching"""
    if not data: return None
    # Use a pepper in prod
    return hashlib.sha256(data.lower().encode()).hexdigest()

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == settings.API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )
