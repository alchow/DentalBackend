from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import hashlib
import os
from app.core.config import settings

# --- Data Encryption (Fernet) ---
_INSECURE_DEFAULT_KEY = "mNDwH60iN1a1xkB6-oJR4lHJ5-dxc-mQII86XXdQC90="
_allow_insecure = os.getenv("ALLOW_INSECURE_DEFAULTS", "").lower() == "true"

_encryption_key = os.getenv("ENCRYPTION_KEY")
if not _encryption_key:
    if _allow_insecure:
        _encryption_key = _INSECURE_DEFAULT_KEY
    else:
        raise RuntimeError(
            "ENCRYPTION_KEY is not set. Set it in your environment or "
            "set ALLOW_INSECURE_DEFAULTS=true for local development."
        )

fernet = Fernet(_encryption_key)

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


def compute_blind_index(data: str) -> str:
    """Alias for get_blind_index for consistency with imports"""
    return get_blind_index(data)


# --- SSN Utilities ---
import re

def parse_ssn_input(ssn: str) -> tuple:
    """
    Parse SSN input and return (full_ssn_digits, last_4).
    
    Input: "123-45-6789" → ("123456789", "6789")
    Input: "123456789" → ("123456789", "6789")
    Input: "6789" → (None, "6789")
    Input: None or "" → (None, None)
    
    Returns: (full_ssn, last_4) tuple
    """
    if not ssn:
        return (None, None)
    
    # Remove dashes, spaces
    digits = re.sub(r'[\s\-]', '', ssn)
    
    if len(digits) == 9:
        # Full SSN
        return (digits, digits[-4:])
    elif len(digits) == 4 and digits.isdigit():
        # Last 4 only
        return (None, digits)
    else:
        # Invalid format
        return (None, None)


def mask_ssn(last_4: str) -> str:
    """Return masked SSN display: '***-**-1234'"""
    if not last_4 or len(last_4) != 4:
        return None
    return f"***-**-{last_4}"


def validate_ssn_format(ssn: str) -> bool:
    """Validate SSN format (full or last-4)"""
    if not ssn:
        return True  # Optional field
    digits = re.sub(r'[\s\-]', '', ssn)
    return len(digits) == 9 or len(digits) == 4

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
