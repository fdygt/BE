from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    username: str
    role: str
    exp: datetime

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "user123",
                "password": "securepass123"
            }
        }
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # detik, bisa disesuaikan
    refresh_token: str | None = None  # Optional, jika ada refresh token

    class Config:
        orm_mode = True
        
class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin123",
                "password": "SecurePass123!"
            }
        }

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }

class PasswordResetRequest(BaseModel):
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset_token_here",
                "new_password": "NewSecurePass123!"
            }
        }

class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code": "data:image/png;base64,iVBORw0K...",
                "backup_codes": [
                    "12345-67890",
                    "11111-22222",
                    "33333-44444"
                ]
            }
        }

class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: Dict
    requires_2fa: Optional[bool] = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_at": "2025-06-02 12:58:40",
                "user": {
                    "id": "adm_12345678",
                    "username": "admin123",
                    "role": "ADMIN",
                    "permissions": ["moderate_users", "view_logs"]
                },
                "requires_2fa": False
            }
        }

# Log creation
import logging
logger = logging.getLogger(__name__)
logger.info(f"""
Auth models initialized:
Time: 2025-06-02 12:58:40
User: fdygt
""")