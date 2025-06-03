from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class Platform(str, Enum):
    DISCORD = "discord"
    WEB = "web"
    API = "api"
    MOBILE = "mobile"

class AdminRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"

class AdminStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class AdminPermission(str, Enum):
    ALL = "all"
    MANAGE_USERS = "manage_users"
    MANAGE_CONTENT = "manage_content"
    VIEW_LOGS = "view_logs"
    MANAGE_SETTINGS = "manage_settings"
    MODERATE_USERS = "moderate_users"
    MANAGE_TRANSACTIONS = "manage_transactions"

class SystemInfo(BaseModel):
    python_version: str = Field(..., description="Python version")
    platform: str = Field(..., description="Platform info (OS, architecture, etc)")
    timezone: str = Field(..., description="Timezone (e.g. UTC)")
    memory: Dict[str, Any] = Field(..., description="Memory info (total, available, percent)")
    disk: Dict[str, Any] = Field(..., description="Disk info (total, free, percent)")
    cpu_percent: float = Field(..., description="CPU usage percent")

    class Config:
        schema_extra = {
            "example": {
                "python_version": "3.11.8 (main, May  8 2024, 13:49:32) [GCC 12.2.0]",
                "platform": "Linux-6.5.0-1017-azure-x86_64-with-glibc2.36",
                "timezone": "UTC",
                "memory": {
                    "total": 16777216,
                    "available": 7340032,
                    "percent": 56.3
                },
                "disk": {
                    "total": 53687091200,
                    "free": 21474836480,
                    "percent": 59.9
                },
                "cpu_percent": 16.7
            }
        }

class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: AdminRole = AdminRole.ADMIN
    permissions: List[AdminPermission] = [AdminPermission.MODERATE_USERS]
    platforms: List[Platform] = Field(default=[Platform.WEB])

    @validator('platforms')
    def validate_platforms(cls, v):
        if not v:
            raise ValueError("At least one platform must be specified")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin123",
                "email": "admin@example.com",
                "password": "SecurePass123!",
                "role": "ADMIN",
                "permissions": ["moderate_users", "view_logs"],
                "platforms": ["web", "discord"]
            }
        }

class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    role: Optional[AdminRole] = None
    permissions: Optional[List[AdminPermission]] = None
    status: Optional[AdminStatus] = None
    platforms: Optional[List[Platform]] = None

    @validator('platforms')
    def validate_platforms(cls, v):
        if v is not None and not v:
            raise ValueError("At least one platform must be specified")
        return v

class AdminResponse(BaseModel):
    id: str
    username: str
    email: str
    role: AdminRole
    permissions: List[AdminPermission]
    status: AdminStatus
    platforms: List[Platform]
    created_at: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:20:48",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    created_by: str = Field(default="fdygt")
    last_login: Optional[datetime] = None
    last_platform: Optional[Platform] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "adm_12345678",
                "username": "admin123",
                "email": "admin@example.com",
                "role": "ADMIN",
                "permissions": ["moderate_users", "view_logs"],
                "status": "ACTIVE",
                "platforms": ["web", "discord"],
                "created_at": "2025-06-02 13:20:48",
                "created_by": "fdygt",
                "last_login": "2025-06-02 13:20:48",
                "last_platform": "web"
            }
        }

class AdminActivityType(str, Enum):
    USER_ACTION = "user_action"
    CONTENT_ACTION = "content_action"
    SYSTEM_ACTION = "system_action"
    TRANSACTION_ACTION = "transaction_action"

class AdminStats(BaseModel):
    admin_id: str
    username: str
    role: AdminRole
    total_actions: int = Field(default=0)
    actions_by_type: Dict[AdminActivityType, int] = Field(default_factory=dict)
    actions_by_platform: Dict[Platform, int] = Field(default_factory=dict)
    active_days: int = Field(default=0)
    last_active: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:20:48",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    average_response_time: float = Field(default=0.0, ge=0.0)  # in seconds
    period_start: datetime
    period_end: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:20:48",
            "%Y-%m-%d %H:%M:%S"
        )
    )

    @validator('success_rate')
    def validate_success_rate(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Success rate must be between 0 and 100")
        return v

    @validator('average_response_time')
    def validate_response_time(cls, v):
        if v < 0:
            raise ValueError("Average response time cannot be negative")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "admin_id": "adm_12345678",
                "username": "admin123",
                "role": "ADMIN",
                "total_actions": 150,
                "actions_by_type": {
                    "user_action": 50,
                    "content_action": 40,
                    "system_action": 30,
                    "transaction_action": 30
                },
                "actions_by_platform": {
                    "web": 80,
                    "discord": 70
                },
                "active_days": 30,
                "last_active": "2025-06-02 13:20:48",
                "success_rate": 98.5,
                "average_response_time": 45.7,
                "period_start": "2025-05-02 00:00:00",
                "period_end": "2025-06-02 13:20:48"
            }
        }

class AdminStatsFilter(BaseModel):
    admin_ids: Optional[List[str]] = None
    roles: Optional[List[AdminRole]] = None
    platforms: Optional[List[Platform]] = None
    activity_types: Optional[List[AdminActivityType]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:20:48",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    min_success_rate: Optional[float] = Field(default=0.0, ge=0.0, le=100.0)
    max_response_time: Optional[float] = Field(default=None, ge=0.0)

class AdminActivity(BaseModel):
    id: str
    admin_id: str
    username: str
    type: AdminActivityType
    action: str = Field(..., description="Description of the action performed")
    platform: Platform
    status: str = Field(default="success")  # success, failed, pending
    target_type: Optional[str] = Field(
        None, 
        description="Type of target (user, content, system, transaction)"
    )
    target_id: Optional[str] = Field(
        None,
        description="ID of the target affected by the action"
    )
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:22:55",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    response_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to complete the action in seconds"
    )

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["success", "failed", "pending"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "act_12345678",
                "admin_id": "adm_12345678",
                "username": "admin123",
                "type": "user_action",
                "action": "Suspended user for violation",
                "platform": "web",
                "status": "success",
                "target_type": "user",
                "target_id": "usr_87654321",
                "metadata": {
                    "reason": "Multiple community guidelines violations",
                    "duration": "7 days",
                    "previous_warnings": 2
                },
                "created_at": "2025-06-02 13:22:55",
                "response_time": 2.5
            }
        }

class AdminActivityFilter(BaseModel):
    admin_ids: Optional[List[str]] = None
    types: Optional[List[AdminActivityType]] = None
    platforms: Optional[List[Platform]] = None
    status: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:22:55",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    min_response_time: Optional[float] = Field(default=None, ge=0.0)
    max_response_time: Optional[float] = Field(default=None, ge=0.0)

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["success", "failed", "pending"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {valid_statuses}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "admin_ids": ["adm_12345678", "adm_87654321"],
                "types": ["user_action", "content_action"],
                "platforms": ["web", "discord"],
                "status": "success",
                "target_type": "user",
                "target_id": "usr_87654321",
                "start_date": "2025-06-01 00:00:00",
                "end_date": "2025-06-02 13:22:55",
                "min_response_time": 0.0,
                "max_response_time": 5.0
            }
        }

class AdminDashboard(BaseModel):
    total_admins: int = Field(default=0)
    active_admins: int = Field(default=0)
    admins_by_role: Dict[AdminRole, int] = Field(default_factory=dict)
    admins_by_platform: Dict[Platform, int] = Field(default_factory=dict)
    total_actions: int = Field(default=0)
    actions_by_type: Dict[AdminActivityType, int] = Field(default_factory=dict)
    actions_by_platform: Dict[Platform, int] = Field(default_factory=dict)
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    average_response_time: float = Field(default=0.0, ge=0.0)
    period_start: datetime
    period_end: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:27:52",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    top_performers: List[Dict] = Field(
        default_factory=list,
        description="List of top performing admins with their stats"
    )
    recent_activities: List[Dict] = Field(
        default_factory=list,
        description="List of recent admin activities"
    )
    system_health: Dict = Field(
        default_factory=lambda: {
            "status": "healthy",
            "uptime": 100.0,
            "last_backup": "2025-06-02 13:27:52",
            "active_sessions": 0,
            "resource_usage": {
                "cpu": 0.0,
                "memory": 0.0,
                "disk": 0.0
            }
        }
    )

    @validator('success_rate')
    def validate_success_rate(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Success rate must be between 0 and 100")
        return v

    @validator('average_response_time')
    def validate_response_time(cls, v):
        if v < 0:
            raise ValueError("Average response time cannot be negative")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "total_admins": 10,
                "active_admins": 8,
                "admins_by_role": {
                    "SUPER_ADMIN": 1,
                    "ADMIN": 4,
                    "MODERATOR": 5
                },
                "admins_by_platform": {
                    "web": 10,
                    "discord": 7,
                    "mobile": 5,
                    "api": 3
                },
                "total_actions": 1500,
                "actions_by_type": {
                    "user_action": 600,
                    "content_action": 400,
                    "system_action": 300,
                    "transaction_action": 200
                },
                "actions_by_platform": {
                    "web": 800,
                    "discord": 500,
                    "mobile": 150,
                    "api": 50
                },
                "success_rate": 98.5,
                "average_response_time": 2.3,
                "period_start": "2025-06-01 00:00:00",
                "period_end": "2025-06-02 13:27:52",
                "top_performers": [
                    {
                        "admin_id": "adm_12345678",
                        "username": "admin123",
                        "role": "ADMIN",
                        "total_actions": 500,
                        "success_rate": 99.5,
                        "average_response_time": 1.8
                    }
                ],
                "recent_activities": [
                    {
                        "id": "act_12345678",
                        "admin_id": "adm_12345678",
                        "username": "admin123",
                        "type": "user_action",
                        "action": "Suspended user for violation",
                        "platform": "web",
                        "status": "success",
                        "created_at": "2025-06-02 13:27:52"
                    }
                ],
                "system_health": {
                    "status": "healthy",
                    "uptime": 99.99,
                    "last_backup": "2025-06-02 13:27:52",
                    "active_sessions": 8,
                    "resource_usage": {
                        "cpu": 45.5,
                        "memory": 62.3,
                        "disk": 78.1
                    }
                }
            }
        }

class AdminSettings(BaseModel):
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email_notifications": True,
            "discord_notifications": True,
            "web_notifications": True,
            "mobile_notifications": False,
            "activity_summary": True,
            "system_alerts": True,
            "user_reports": True,
            "content_updates": True
        }
    )
    display_preferences: Dict[str, str] = Field(
        default_factory=lambda: {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "time_format": "24h"
        }
    )
    action_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "confirm_actions": True,
            "auto_refresh": True,
            "show_tooltips": True,
            "compact_view": False
        }
    )
    security_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "two_factor_auth": True,
            "session_timeout": True,
            "ip_whitelist": False,
            "audit_logging": True
        }
    )
    platform_preferences: Dict[Platform, Dict] = Field(
        default_factory=lambda: {
            "web": {
                "default_view": "dashboard",
                "items_per_page": 25,
                "show_quick_actions": True
            },
            "discord": {
                "auto_response": True,
                "dm_notifications": True,
                "command_prefix": "!"
            },
            "mobile": {
                "push_notifications": False,
                "data_saving": True,
                "offline_mode": False
            },
            "api": {
                "auto_retry": True,
                "debug_mode": False,
                "rate_limit": 1000
            }
        }
    )
    last_updated: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:31:14",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    updated_by: str = Field(default="fdygt")

    @validator('platform_preferences')
    def validate_platform_preferences(cls, v):
        valid_platforms = [p.value for p in Platform]
        for platform in v.keys():
            if platform not in valid_platforms:
                raise ValueError(f"Invalid platform: {platform}. Must be one of: {valid_platforms}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "notification_preferences": {
                    "email_notifications": True,
                    "discord_notifications": True,
                    "web_notifications": True,
                    "mobile_notifications": False,
                    "activity_summary": True,
                    "system_alerts": True,
                    "user_reports": True,
                    "content_updates": True
                },
                "display_preferences": {
                    "theme": "light",
                    "language": "en",
                    "timezone": "UTC",
                    "date_format": "YYYY-MM-DD",
                    "time_format": "24h"
                },
                "action_preferences": {
                    "confirm_actions": True,
                    "auto_refresh": True,
                    "show_tooltips": True,
                    "compact_view": False
                },
                "security_preferences": {
                    "two_factor_auth": True,
                    "session_timeout": True,
                    "ip_whitelist": False,
                    "audit_logging": True
                },
                "platform_preferences": {
                    "web": {
                        "default_view": "dashboard",
                        "items_per_page": 25,
                        "show_quick_actions": True
                    },
                    "discord": {
                        "auto_response": True,
                        "dm_notifications": True,
                        "command_prefix": "!"
                    },
                    "mobile": {
                        "push_notifications": False,
                        "data_saving": True,
                        "offline_mode": False
                    },
                    "api": {
                        "auto_retry": True,
                        "debug_mode": False,
                        "rate_limit": 1000
                    }
                },
                "last_updated": "2025-06-02 13:31:14",
                "updated_by": "fdygt"
            }
        }

# Log creation
import logging
logger = logging.getLogger(__name__)
logger.info(f"""
Admin models initialized:
Time: 2025-06-02 13:31:14
User: fdygt
""")