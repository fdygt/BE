from typing import Optional
from fastapi import Depends, HTTPException
from datetime import datetime, UTC
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Variable untuk menyimpan instance bot
_bot = None

def set_bot(bot):
    """
    Set bot instance untuk digunakan di seluruh aplikasi
    Args:
        bot: Instance dari bot yang akan digunakan
    """
    global _bot
    _bot = bot
    
    logger.debug(f"""
        Setting bot instance:
        Bot: {bot.__class__.__name__}
        Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
    """)

def get_bot():
    """
    Mendapatkan instance bot yang telah di-set
    Returns:
        Bot instance atau None jika belum di-set
    Raises:
        HTTPException: Jika bot belum diinisialisasi
    """
    if _bot is None:
        raise HTTPException(
            status_code=500,
            detail="Bot instance not initialized"
        )
    return _bot

# Re-export dependencies yang sering digunakan
from .auth import get_current_user, verify_admin
from .database import SessionLocal, get_db
from .cache import cache_manager
from .redis import redis_client
from .logger import logger
from .validation import Validator
from .audit import audit_logger
from .rate_limiter import rate_limiter

__all__ = [
    "set_bot",
    "get_bot",
    "get_current_user",
    "verify_admin",
    "SessionLocal",
    "get_db",
    "cache_manager",
    "redis_client", 
    "logger",
    "Validator",
    "audit_logger",
    "rate_limiter"
]