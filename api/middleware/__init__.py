from fastapi import Request, Response, HTTPException, Depends
from functools import wraps
from datetime import datetime, UTC
import logging
from typing import Callable, Dict, Any, Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Constants
CURRENT_TIMESTAMP = "2025-06-03 01:44:57"  # Updated sesuai waktu yang diberikan
CURRENT_USER = "fdygt"  # User yang diberikan

def get_current_time() -> str:
    """Get current timestamp in consistent format"""
    return CURRENT_TIMESTAMP

def get_current_user() -> str:
    """Get current user's login"""
    return CURRENT_USER

def format_log_message(message: str) -> str:
    """Format log message with timestamp and user"""
    return f"""
    {message}
    Timestamp: {CURRENT_TIMESTAMP}
    User: {CURRENT_USER}
    """

def skip_auth(func: Callable) -> Callable:
    """Decorator to skip authentication for specific routes"""
    setattr(func, "skip_auth", True)
    return func

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Verify JWT token and return username"""
    try:
        token = credentials.credentials
        
        # Verify token
        payload = jwt.decode(
            token,
            "your-secret-key",  # Use actual secret key from config
            algorithms=["HS256"]
        )
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
            
        return username
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
        
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

def log_request(request: Request, message: str) -> None:
    """Log request details with formatted message"""
    logger.info(format_log_message(f"""
    {message}
    Path: {request.url.path}
    Method: {request.method}
    Client: {request.client.host}
    Time: {CURRENT_TIMESTAMP}
    User-Agent: {request.headers.get("user-agent")}
    """))

# Import all middleware components
from .auth import (
    AuthMiddleware,
    get_token_from_header
)

from .logging import (
    LoggingMiddleware,
    log_request,
    log_response,
    format_request_log,
    format_response_log
)

from .error_handling import (
    ErrorHandlingMiddleware,
    handle_http_exception,
    handle_validation_error,
    handle_database_error
)

from .rate_limiting import (
    RateLimitMiddleware,
    check_rate_limit,
    update_rate_limit,
    get_rate_limit_key
)

from .caching import (
    CacheMiddleware,
    get_cache_key,
    set_cache,
    get_cache,
    clear_cache
)

from .compression import CompressionMiddleware
from .security import SecurityMiddleware
from .metrics import MetricsMiddleware
from .validation import ValidationMiddleware

def setup_middleware(app):
    """Setup all middleware for the application"""
    try:
        # Urutan middleware penting! Yang paling dasar dulu
        
        # 1. Metrics & Logging (harus pertama untuk mencatat semua request)
        app.add_middleware(MetricsMiddleware)
        app.add_middleware(LoggingMiddleware)
        
        # 2. Security & Validation
        app.add_middleware(SecurityMiddleware)
        app.add_middleware(ValidationMiddleware)
        
        # 3. Compression (setelah validasi, sebelum caching)
        app.add_middleware(CompressionMiddleware)
        
        # 4. Error Handling (sebelum rate limiting dan auth)
        app.add_middleware(ErrorHandlingMiddleware)
        
        # 5. Performance & Caching
        app.add_middleware(RateLimitMiddleware)
        app.add_middleware(CacheMiddleware)
        
        # 6. Auth (terakhir, setelah semua middleware lain)
        app.add_middleware(AuthMiddleware)
        
        logger.info(format_log_message("""
        Middleware setup complete:
        1. Metrics Middleware
        2. Logging Middleware
        3. Security Middleware
        4. Validation Middleware
        5. Compression Middleware
        6. Error Handling Middleware
        7. Rate Limiting Middleware
        8. Cache Middleware
        9. Auth Middleware
        """))
        
    except Exception as e:
        logger.error(format_log_message(f"""
        Failed to setup middleware:
        Error: {str(e)}
        """))
        raise

# Export all middleware components
__all__ = [
    # Auth middleware
    "AuthMiddleware",
    "get_token_from_header",
    
    # Logging middleware
    "LoggingMiddleware",
    "log_request",
    "log_response",
    "format_request_log",
    "format_response_log",
    
    # Error handling middleware
    "ErrorHandlingMiddleware",
    "handle_http_exception",
    "handle_validation_error", 
    "handle_database_error",
    
    # Rate limiting middleware 
    "RateLimitMiddleware",
    "check_rate_limit",
    "update_rate_limit",
    "get_rate_limit_key",
    
    # Cache middleware
    "CacheMiddleware",
    "get_cache_key",
    "set_cache",
    "get_cache",
    "clear_cache",
    
    # Additional middleware
    "CompressionMiddleware",
    "SecurityMiddleware",
    "MetricsMiddleware",
    "ValidationMiddleware",
    
    # Setup function
    "setup_middleware",
    
    # Utility functions
    "get_current_time",
    "get_current_user", 
    "format_log_message",
    "skip_auth",
    
    # Constants
    "CURRENT_TIMESTAMP",
    "CURRENT_USER",
    
    # Security
    "security"
]