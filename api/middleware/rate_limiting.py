from datetime import datetime, UTC
import logging
from typing import Optional, Tuple, Dict, Any
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from ..service.rate_limit_service import RateLimitService
from ..service.auth_service import AuthService
from ..models.rate_limit import RateLimit

logger = logging.getLogger(__name__)

# Initialize services at module level for exported functions
_rate_limit_service = RateLimitService()

async def check_rate_limit(user_id: str, endpoint: str, ip_address: str) -> Tuple[bool, Dict]:
    """
    Check if the request is within rate limit.
    Returns (allowed: bool, limit_info: dict)
    """
    return await _rate_limit_service.check_rate_limit(user_id, endpoint, ip_address)

async def update_rate_limit(user_id: str, endpoint: str, ip_address: str):
    """
    Log the request to update the rate limiting data store.
    """
    return await _rate_limit_service.log_request(user_id, endpoint, ip_address)

def get_rate_limit_key(user_id: str, endpoint: str, ip_address: str) -> str:
    """
    Generate a unique key for rate limiting purposes.
    """
    return f"{user_id}:{endpoint}:{ip_address}"

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_service = RateLimitService()
        self.auth_service = AuthService()
        self.startup_time = datetime.now(UTC)
        logger.info("""
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:44:44
Current User's Login: fdygt
RateLimitMiddleware initialized
        """)

    async def get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        try:
            # Get token from header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None

            token = auth_header.split(" ")[1]
            
            # Verify token
            is_valid, token_data = await self.auth_service.verify_token(token)
            if not is_valid or not token_data:
                return None

            return token_data.username

        except Exception as e:
            logger.error("""
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:44:44
Current User's Login: fdygt
Error extracting user ID: {str(e)}
            """)
            return None

    async def dispatch(self, request: Request, call_next):
        try:
            # Get user ID and IP
            user_id = await self.get_user_id(request) or "anonymous"
            ip_address = request.client.host
            endpoint = request.url.path

            # Skip rate limiting for static files and health checks
            if endpoint.startswith(("/static/", "/public/", "/health")):
                return await call_next(request)

            # Check rate limit
            is_allowed, limit_info = await self.rate_limit_service.check_rate_limit(
                user_id=user_id,
                endpoint=endpoint,
                ip_address=ip_address
            )

            if not is_allowed:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Too Many Requests",
                        "reset": limit_info["reset"],
                        "limit": limit_info["limit"],
                        "remaining": 0,
                        "retry_after": limit_info["window"]
                    }
                )

            # Log request
            await self.rate_limit_service.log_request(
                user_id=user_id,
                endpoint=endpoint,
                ip_address=ip_address
            )

            # Add rate limit headers
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
            response.headers["X-RateLimit-Reset"] = limit_info["reset"]

            return response

        except HTTPException as he:
            # Re-raise HTTP exceptions (including our rate limit exception)
            raise he
        except Exception as e:
            logger.error("""
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:44:44
Current User's Login: fdygt
Rate limit middleware error: {str(e)}
            """)
            raise HTTPException(
                status_code=500,
                detail="Internal server error in rate limiting"
            )

    async def handle_exceeded_rate_limit(
        self,
        request: Request,
        limit_info: dict
    ) -> Response:
        """Handle rate limit exceeded cases"""
        return Response(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": "Rate limit exceeded",
                "reset": limit_info["reset"],
                "limit": limit_info["limit"],
                "remaining": 0,
                "retry_after": limit_info["window"]
            },
            headers={
                "X-RateLimit-Limit": str(limit_info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": limit_info["reset"],
                "Retry-After": str(limit_info["window"])
            }
        )