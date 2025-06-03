import logging
import redis
from datetime import datetime, UTC
from typing import Optional

from ..config.redis import REDIS_CONFIG

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self._redis = None
        self.startup_time = datetime.now(UTC)
        self._init_redis()
        
    def _init_redis(self):
        """Initialize Redis connection with retry mechanism"""
        try:
            self._redis = redis.Redis(**REDIS_CONFIG)
            self._redis.ping()
            logger.info(f"""
            Redis initialized successfully:
            Time: {datetime.now(UTC)}
            Host: {REDIS_CONFIG['host']}
            Port: {REDIS_CONFIG['port']}
            DB: {REDIS_CONFIG['db']}
            User: fdygt
            """)
        except redis.ConnectionError as e:
            logger.warning(f"""
            Redis connection failed, will continue without Redis:
            Error: {str(e)}
            Time: {datetime.now(UTC)}
            User: fdygt
            """)
            self._redis = None
        except Exception as e:
            logger.error(f"""
            Redis initialization error:
            Error: {str(e)}
            Time: {datetime.now(UTC)}
            User: fdygt
            """)
            self._redis = None

    @property
    def redis(self) -> Optional[redis.Redis]:
        """Get Redis connection if available"""
        return self._redis

    def is_redis_available(self) -> bool:
        """Check if Redis is available"""
        if not self._redis:
            return False
        try:
            self._redis.ping()
            return True
        except:
            return False