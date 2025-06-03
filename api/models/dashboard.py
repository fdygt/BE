from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any  # Tambahkan Any di sini
from datetime import datetime
from enum import Enum

class SystemInfo(BaseModel):
    """System information model"""
    version: str = "1.0.0"
    uptime: float
    start_time: datetime
    environment: str
    database_status: str
    cache_status: str
    total_users: Optional[int] = 0
    total_products: Optional[int] = 0
    total_transactions: Optional[int] = 0
    system_stats: Optional[Dict[str, Any]] = {}  # Perbaiki tipe Dict
    recent_activities: Optional[List[Dict[str, Any]]] = []  # Perbaiki tipe Dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0.0",
                "uptime": 3600.0,
                "start_time": "2025-06-02T14:29:49",
                "environment": "production",
                "database_status": "connected",
                "cache_status": "connected",
                "total_users": 100,
                "total_products": 50,
                "total_transactions": 1000,
                "system_stats": {
                    "cpu_usage": "25%",
                    "memory_usage": "40%",
                    "disk_usage": "60%"
                },
                "recent_activities": [
                    {
                        "type": "user_login",
                        "timestamp": "2025-06-02T14:29:49",
                        "details": "User login successful"
                    }
                ]
            }
        }

class UserActivity(BaseModel):
    action: str
    timestamp: datetime = Field(default_factory=lambda: datetime.strptime("2025-06-02 14:29:49", "%Y-%m-%d %H:%M:%S"))
    details: Optional[Dict[str, Any]] = None  # Perbaiki tipe Dict
    status: str = "completed"

class SystemStatus(BaseModel):
    name: str
    id: str
    uptime: str
    guilds: int
    last_updated: datetime = Field(default_factory=lambda: datetime.strptime("2025-06-02 14:29:49", "%Y-%m-%d %H:%M:%S"))
    version: str = "1.0.0"

class UserStats(BaseModel):
    total_transactions: int = 0
    total_balance: float = 0.0
    stock_count: int = 0
    last_activity: Optional[UserActivity] = None

class StockAlert(BaseModel):
    product_code: str
    product_name: str
    current_stock: int
    min_stock: int
    alert_level: str
    last_updated: datetime = Field(default_factory=lambda: datetime.strptime("2025-06-02 14:29:49", "%Y-%m-%d %H:%M:%S"))

class DashboardStats(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.strptime("2025-06-02 14:29:49", "%Y-%m-%d %H:%M:%S"))
    user: Dict[str, Any]  # Perbaiki dari 'any' menjadi 'Any'
    system: SystemStatus
    stats: UserStats
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-06-02 14:29:49",
                "user": {
                    "username": "fdygt",
                    "last_activity": []
                },
                "system": {
                    "name": "BOT_NAME",
                    "id": "BOT_ID",
                    "uptime": "10:30:15",
                    "guilds": 1,
                    "last_updated": "2025-06-02 14:29:49",
                    "version": "1.0.0"
                },
                "stats": {
                    "total_transactions": 0,
                    "total_balance": 0.0,
                    "stock_count": 0,
                    "last_activity": None
                }
            }
        }

class UserDashboard(BaseModel):
    username: str = "fdygt"
    timestamp: datetime = Field(default_factory=lambda: datetime.strptime("2025-06-02 14:29:49", "%Y-%m-%d %H:%M:%S"))
    stats: UserStats
    recent_transactions: List[Dict[str, Any]] = []  # Perbaiki tipe Dict
    stock_alerts: List[StockAlert] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "fdygt",
                "timestamp": "2025-06-02 14:29:49",
                "stats": {
                    "total_transactions": 0,
                    "total_balance": 0.0,
                    "stock_count": 0,
                    "last_activity": None
                },
                "recent_transactions": [],
                "stock_alerts": []
            }
        }

class DashboardSettings(BaseModel):
    show_balance: bool = True
    show_transactions: bool = True
    show_stock_alerts: bool = True
    refresh_interval: int = 30  # seconds
    theme: str = "light"
    notifications_enabled: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "show_balance": True,
                "show_transactions": True,
                "show_stock_alerts": True,
                "refresh_interval": 30,
                "theme": "light",
                "notifications_enabled": True
            }
        }