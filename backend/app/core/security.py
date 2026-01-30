from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import hashlib
import os
from app.core.config import settings

# --- Data Encryption (Fernet) ---
DEV_KEY = os.getenv("ENCRYPTION_KEY", "mNDwH60iN1a1xkB6-oJR4lHJ5-dxc-mQII86XXdQC90=")
fernet = Fernet(DEV_KEY)

def encrypt_data(data: str) -> str:
    if not data: return data
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    if not data: return data
    return fernet.decrypt(data.encode()).decode()

def get_blind_index(data: str) -> str:
    """Deterministic hash for searching"""
    if not data: return None
    return hashlib.sha256(data.lower().encode()).hexdigest()

# --- Password & API Key Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_api_key_hash(api_key: str) -> str:
    """Hash API key for storage/comparison (using SHA256)"""
    return hashlib.sha256(api_key.encode()).hexdigest()

# --- JWT Token ---
ALGORITHM = "HS256"

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: timedelta = None,
    token_type: str = "access"
) -> str:
    """
    Create a JWT token.
    
    Args:
        subject: The subject (usually user ID)
        expires_delta: Token expiration time
        token_type: Type of token ('access' or 'password_reset')
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject),
        "type": token_type
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Returns the payload dict or raises an exception if invalid.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
