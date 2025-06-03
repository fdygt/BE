from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Any, Type, Tuple
import logging
from datetime import datetime, UTC
import traceback
import sys
from uuid import uuid4
import json

from ..service.error_handling_service import ErrorHandlingService
from ..service.notification_service import NotificationService
from ..models.notifications import (
    Notification,
    NotificationType,
    NotificationPriority,
    NotificationChannel,
    NotificationStatus
)

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.error_service = ErrorHandlingService()
        self.notification_service = NotificationService()
        self.startup_time = datetime.now(UTC)
        
        # Error mapping
        self.status_codes = {
            RequestValidationError: 422,
            ValueError: 400,
            KeyError: 400,
            HTTPException: None,  # Use exception's status_code
            Exception: 500
        }
        
        # Notification settings
        self.NOTIFY_ON_STATUS = {500, 503}  # Status codes that trigger notifications
        self.ERROR_AGGREGATION_WINDOW = 300  # 5 minutes
        self.ERROR_NOTIFICATION_THRESHOLD = 5  # Errors within window to trigger notification
        
        # Error tracking
        self.error_counts = {}
        
        logger.info("""
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:13:01
Current User's Login: fdygt
ErrorHandlingMiddleware initialized
        """)

    def _get_error_details(
        self,
        request: Request,
        exc: Exception
    ) -> Dict[str, Any]:
        """Get detailed error information"""
        error_id = str(uuid4())
        timestamp = datetime.now(UTC)
        
        # Get error location
        tb = traceback.extract_tb(sys.exc_info()[2])
        location = f"{tb[-1].filename}:{tb[-1].lineno}" if tb else "Unknown"
        
        # Get request context
        context = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host,
            "headers": dict(request.headers)
        }
        
        # Get user context if available
        user_id = getattr(request.state, "user", {}).get("id", "anonymous")
        
        return {
            "id": error_id,
            "timestamp": timestamp,
            "type": type(exc).__name__,
            "message": str(exc),
            "location": location,
            "traceback": traceback.format_exc(),
            "context": context,
            "user_id": user_id
        }

def handle_http_exception(request, exc: HTTPException):
    logger.error("""
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:13:01
Current User's Login: fdygt
HTTPException: {exc.detail} | Status: {exc.status_code}
    """)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

def handle_validation_error(request, exc: RequestValidationError):
    logger.error("""
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:13:01
Current User's Login: fdygt
Validation error: {exc.errors()}
    """)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

def handle_database_error(request, exc: Exception):
    logger.error("""
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:13:01
Current User's Login: fdygt
Database error: {str(exc)}
{traceback.format_exc()}
    """)
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred."}
    )

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
            
        except Exception as exc:
            try:
                # Get error details
                error_details = self._get_error_details(request, exc)
                
                # Get status code
                status_code = (
                    getattr(exc, "status_code", None) or
                    self.status_codes.get(type(exc)) or
                    self.status_codes.get(Exception)
                )
                
                # Log error
                log_level = logging.ERROR if status_code >= 500 else logging.WARNING
                logger.log(log_level, """
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:13:01
Current User's Login: fdygt
Error Details: {json.dumps(error_details, default=str)}
                """)
                
                # Check if should notify
                if await self._should_notify(error_details["type"], status_code):
                    await self._create_error_notification(error_details, status_code)
                
                # Get response data
                response_data = self._get_response_data(error_details, status_code)
                
                # Create response
                response = JSONResponse(
                    status_code=status_code,
                    content=response_data
                )
                
                # Add headers
                response.headers["X-Error-ID"] = error_details["id"]
                response.headers["X-Error-Type"] = error_details["type"]
                
                return response
                
            except Exception as e:
                # Fallback error handling
                logger.error("""
Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-06-03 12:13:01
Current User's Login: fdygt
Error in error handler: {str(e)}
                """)
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "type": "InternalServerError",
                            "message": "An unexpected error occurred"
                        }
                    }
                )

    # ... rest of the methods remain the same but with updated log formats