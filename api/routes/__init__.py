from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, UTC
from pathlib import Path
import logging
import sys
import platform
import psutil
from typing import Dict, Any

from ..middleware.auth import skip_auth
from ..config import config, API_VERSION
from ..models.dashboard import SystemInfo

# Initialize router and logger
router = APIRouter()
logger = logging.getLogger(__name__)

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

# Import all routers
from .auth import router as auth_router
from .admin import router as admin_router
from .balance import router as balance_router
from .dashboard import router as dashboard_router
from .stock import router as stock_router
from .transactions import router as transactions_router
from .user import router as user_router
from .product import router as product_router

# Router configurations with metadata
ROUTER_CONFIGS = [
    {
        "router": auth_router,
        "prefix": "/auth",
        "tags": ["Auth"],
        "responses": {
            401: {"description": "Unauthorized"},
            400: {"description": "Bad Request"}
        }
    },
    {
        "router": admin_router,
        "prefix": "/admin",
        "tags": ["Admin"],
        "responses": {
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"}
        }
    },
    {
        "router": balance_router,
        "prefix": "/balance",
        "tags": ["Balance"],
        "responses": {
            404: {"description": "Balance not found"}
        }
    },
    {
        "router": dashboard_router,
        "prefix": "/dashboard",
        "tags": ["Dashboard"],
        "responses": {
            404: {"description": "Dashboard data not found"}
        }
    },
    {
        "router": stock_router,
        "prefix": "/stock",
        "tags": ["Stock"],
        "responses": {
            404: {"description": "Stock not found"}
        }
    },
    {
        "router": transactions_router,
        "prefix": "/transactions",
        "tags": ["Transactions"],
        "responses": {
            404: {"description": "Transaction not found"}
        }
    },
    {
        "router": user_router,
        "prefix": "/users",
        "tags": ["Users"],
        "responses": {
            404: {"description": "User not found"},
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"}
        }
    },
    {
        "router": product_router,
        "prefix": "/products",
        "tags": ["Products"],
        "responses": {
            404: {"description": "Product not found"}
        }
    }
]

# Register all routers with their configurations
for router_config in ROUTER_CONFIGS:
    router.include_router(**router_config)

def get_system_info() -> SystemInfo:
    """Get system information with fallbacks"""
    try:
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "percent": round(memory.percent, 2)
        }
    except:
        memory_info = {"error": "Memory stats unavailable"}
        
    try:
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "free": disk.free,
            "percent": round(disk.percent, 2)
        }
    except:
        disk_info = {"error": "Disk stats unavailable"}
        
    try:
        cpu_percent = round(psutil.cpu_percent(interval=0.1), 2)
    except:
        cpu_percent = 0.0
        
    return SystemInfo(
        python_version=sys.version,
        platform=platform.platform(),
        timezone="UTC",
        memory=memory_info,
        disk=disk_info,
        cpu_percent=cpu_percent
    )

@router.get("/health")
@skip_auth()  # Ditambahkan tanda kurung
async def health_check():
    """API health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
        "version": API_VERSION,
        "user": "fdygt"
    }

@router.get("/system")
async def system_status():
    """Get detailed system status"""
    try:
        logger.info(f"""
        System status check:
        Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
        User: fdygt
        """)
        
        return {
            "system": get_system_info().dict(),
            "user": "fdygt",
            "status": "ok",
            "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logger.error(f"""
        System status error:
        Error: {str(e)}
        Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
        User: fdygt
        """)
        raise HTTPException(
            status_code=500,
            detail="System status check failed"
        )

@router.get("/version")
@skip_auth()  # Ditambahkan tanda kurung
async def get_version():
    """Get API version information"""
    return {
        "version": API_VERSION,
        "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
        "environment": config.get_environment(),
        "min_client_version": "1.0.0"
    }

# Export all routers
__all__ = [
    "router",
    "auth_router",
    "admin_router",
    "balance_router",
    "dashboard_router",
    "stock_router",
    "transactions_router",
    "user_router",
    "product_router"
]