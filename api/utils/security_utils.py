import bcrypt
import base64
import jwt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from typing import Tuple, Optional, Dict, Any

from ..config import config

def hash_password(password: str) -> Tuple[str, str]:
    """
    Hash password with salt
    Returns: (hashed_password, salt)
    """
    salt = generate_salt()
    hashed = bcrypt.hashpw(
        password.encode('utf-8'),
        salt
    )
    return base64.b64encode(hashed).decode('utf-8'), \
           base64.b64encode(salt).decode('utf-8')

def verify_password(
    password: str,
    hashed_password: str,
    salt: str
) -> bool:
    """Verify password against hash"""
    try:
        salt_bytes = base64.b64decode(salt.encode('utf-8'))
        hashed_bytes = base64.b64decode(hashed_password.encode('utf-8'))
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_bytes
        )
    except:
        return False

def generate_salt() -> bytes:
    """Generate random salt"""
    return bcrypt.gensalt()

def encrypt_data(data: str) -> Optional[str]:
    """Encrypt sensitive data"""
    try:
        f = Fernet(config.ENCRYPTION_KEY)
        return f.encrypt(data.encode()).decode()
    except:
        return None

def decrypt_data(encrypted_data: str) -> Optional[str]:
    """Decrypt sensitive data"""
    try:
        f = Fernet(config.ENCRYPTION_KEY)
        return f.decrypt(encrypted_data.encode()).decode()
    except:
        return None

def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT token
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=config.TOKEN_EXPIRATION_SECONDS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode JWT token
    Args:
        token: JWT token to decode
    Returns:
        Decoded token data
    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])