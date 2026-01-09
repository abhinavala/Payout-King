"""
Security utilities for authentication and encryption.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from cryptography.fernet import Fernet
import base64
import hashlib

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        # Handle both passlib format and raw bcrypt
        if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
        return False
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt directly.
    
    Bcrypt has a 72-byte limit, so we truncate if necessary.
    """
    # Bcrypt has a 72-byte limit, truncate if longer
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_encryption_key() -> bytes:
    """Get encryption key for API tokens."""
    # Derive a 32-byte key from the settings key
    key = settings.ENCRYPTION_KEY.encode()
    # Use SHA256 to ensure 32 bytes
    key_hash = hashlib.sha256(key).digest()
    return base64.urlsafe_b64encode(key_hash)


def encrypt_api_token(token: str) -> str:
    """Encrypt an API token before storing in database."""
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()


def decrypt_api_token(encrypted_token: str) -> str:
    """Decrypt an API token from database."""
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()

