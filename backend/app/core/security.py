from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from cryptography.fernet import Fernet, InvalidToken
import os
import logging

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    payload = decode_token(token)
    
    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (convenience dependency)."""
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current superuser - require superuser privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


# ============================================================================
# Encryption at Rest
# ============================================================================

# Fernet cipher instance (lazy loaded)
_fernet_cipher: Optional[Fernet] = None


def _get_fernet_cipher() -> Fernet:
    """Get or create Fernet cipher instance."""
    global _fernet_cipher
    
    if _fernet_cipher is None:
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY not set. Generate one with: "
                "python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )
        
        try:
            _fernet_cipher = Fernet(encryption_key.encode())
        except Exception as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY format: {e}")
    
    return _fernet_cipher


def is_encryption_enabled() -> bool:
    """Check if encryption is enabled (ENCRYPTION_KEY is set)."""
    return os.getenv("ENCRYPTION_KEY") is not None


def encrypt_data(plain_text: str) -> str:
    """
    Encrypt plain text data using Fernet symmetric encryption.
    
    Args:
        plain_text: The data to encrypt
    
    Returns:
        Base64-encoded encrypted data (as string)
    
    Raises:
        ValueError: If ENCRYPTION_KEY not configured
    """
    if not plain_text:
        return plain_text
    
    try:
        cipher = _get_fernet_cipher()
        encrypted_bytes = cipher.encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise ValueError(f"Failed to encrypt data: {e}")


def decrypt_data(cipher_text: str) -> str:
    """
    Decrypt encrypted data using Fernet symmetric encryption.
    
    Args:
        cipher_text: Base64-encoded encrypted data
    
    Returns:
        Decrypted plain text
    
    Raises:
        ValueError: If ENCRYPTION_KEY not configured or decryption fails
    """
    if not cipher_text:
        return cipher_text
    
    try:
        cipher = _get_fernet_cipher()
        decrypted_bytes = cipher.decrypt(cipher_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except InvalidToken:
        logger.error("Invalid encryption token - data may be corrupted or key changed")
        raise ValueError("Failed to decrypt data: invalid token")
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise ValueError(f"Failed to decrypt data: {e}")


def encrypt_if_enabled(plain_text: str) -> str:
    """Encrypt data only if encryption is enabled, otherwise return as-is."""
    if is_encryption_enabled():
        return encrypt_data(plain_text)
    return plain_text


def decrypt_if_enabled(cipher_text: str) -> str:
    """Decrypt data only if encryption is enabled, otherwise return as-is."""
    if is_encryption_enabled():
        return decrypt_data(cipher_text)
    return cipher_text


# ============================================================================
# License Validation
# ============================================================================

def generate_license_key() -> str:
    """
    Generate a new license key for the application.
    
    For self-hosted open-source version, this returns a placeholder.
    Can be extended with actual license generation logic.
    
    Returns:
        Generated license key
    """
    import secrets
    import hashlib
    
    # Generate random bytes
    random_bytes = secrets.token_bytes(32)
    
    # Create a hash
    hash_obj = hashlib.sha256(random_bytes)
    hash_hex = hash_obj.hexdigest()
    
    # Format as license key (XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX)
    key_parts = [hash_hex[i:i+4] for i in range(0, 32, 4)]
    license_key = "-".join(key_parts)
    
    return f"CHST-{license_key}"


def is_license_valid(provided_key: Optional[str] = None) -> bool:
    """
    Validate license key.
    
    For self-hosted open-source version:
    - Returns True if no LICENSE_KEY is set (open mode)
    - Returns True if provided_key matches LICENSE_KEY
    - Can be extended with more complex validation logic
    
    Args:
        provided_key: License key to validate (optional, reads from env if not provided)
    
    Returns:
        True if license is valid or not required, False otherwise
    """
    required_key = os.getenv("LICENSE_KEY")
    
    # If no license key is required, allow access (open-source mode)
    if not required_key:
        return True
    
    # Use provided key or read from environment
    key_to_check = provided_key or os.getenv("USER_LICENSE_KEY")
    
    # Check if key matches
    if not key_to_check:
        return False
    
    # Simple validation: check prefix and format
    if not key_to_check.startswith("CHST-"):
        return False
    
    # Check if matches required key
    return key_to_check == required_key
