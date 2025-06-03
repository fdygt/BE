import sqlite3
import logging
from typing import Optional, Dict
from datetime import datetime, UTC

logger = logging.getLogger(__name__)

class DatabaseUtils:
    """Utility class for database operations"""
    _instance = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseUtils, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._conn:
            self.startup_time = datetime.now(UTC)
            logger.info(f"""
            DatabaseUtils initialized:
            Time: {self.startup_time}
            User: fdygt
            """)
            self._init_connection()

    def _init_connection(self):
        """Initialize database connection"""
        try:
            self._conn = sqlite3.connect('shop.db', check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            cursor = self._conn.cursor()
            
            # Enable foreign keys and WAL mode
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            
            # Create admin table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    discord_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self._conn.commit()
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        if not self._conn:
            self._init_connection()
        return self._conn

    def get_admin(self, discord_id: str) -> Optional[Dict]:
        """Get admin data from database"""
        try:
            cursor = self._conn.cursor()
            
            cursor.execute("""
                SELECT discord_id, username, is_active 
                FROM admins 
                WHERE discord_id = ? COLLATE binary
            """, (discord_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    "discord_id": result[0],
                    "username": result[1],
                    "is_active": bool(result[2])
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting admin: {e}")
            return None

    def create_admin(self, discord_id: str, username: str) -> bool:
        """Create new admin"""
        try:
            cursor = self._conn.cursor()
            
            cursor.execute("""
                INSERT INTO admins (discord_id, username)
                VALUES (?, ?)
                ON CONFLICT(discord_id) DO UPDATE SET
                    username = excluded.username,
                    updated_at = CURRENT_TIMESTAMP
            """, (discord_id, username))
            
            self._conn.commit()
            logger.info(f"Admin created/updated successfully: {discord_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating admin: {e}")
            self._conn.rollback()
            return False

    def update_admin_status(self, discord_id: str, is_active: bool) -> bool:
        """Update admin active status"""
        try:
            cursor = self._conn.cursor()
            
            cursor.execute("""
                UPDATE admins 
                SET is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE discord_id = ?
            """, (is_active, discord_id))
            
            self._conn.commit()
            logger.info(f"Admin status updated: {discord_id} -> {is_active}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating admin status: {e}")
            self._conn.rollback()
            return False

    def close(self):
        """Close database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("Database connection closed")

# Singleton instance
db_utils = DatabaseUtils()