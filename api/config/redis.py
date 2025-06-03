import os
from datetime import timedelta

REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "password": os.getenv("REDIS_PASSWORD", "YourStrongPasswordHere"),
    "db": int(os.getenv("REDIS_DB", 0)),
    "decode_responses": True,
    "socket_timeout": 5,
    "retry_on_timeout": True,
    "health_check_interval": 30,
}

# Cache settings
CACHE_TTL = timedelta(minutes=15)
CACHE_PREFIX = "shop_bot:"

# Rate limiting
RATE_LIMIT_PREFIX = "rate_limit:"
DEFAULT_RATE_LIMIT = "100/minute"

# Session
SESSION_PREFIX = "session:"
SESSION_TTL = timedelta(days=1)

__all__ = [
    "REDIS_CONFIG",
    "CACHE_TTL",
    "CACHE_PREFIX",
    "RATE_LIMIT_PREFIX",
    "DEFAULT_RATE_LIMIT",
    "SESSION_PREFIX",
    "SESSION_TTL"
]