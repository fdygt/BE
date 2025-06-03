# Current Date and Time
Current_Date = "2025-06-02 14:21:18"
Current_User = "fdygt"

# API Version
API_VERSION = "v1"  # Tambahkan ini di bagian atas

# Import all configurations
from .settings import config as settings_config
from .security import (
    JWT_SECRET_KEY,
    TOKEN_EXPIRATION_SECONDS,
    PASSWORD_HASH_SCHEME
)
from .database import (
    DATABASE_POOL_SIZE,
    DATABASE_TIMEOUT
)
from .cache import (
    CACHE_CONFIG,
    CACHE_TTL,
    CACHE_KEY_PATTERNS,
    CACHE_INVALIDATION_RULES,
    CACHE_WARMING,
    CACHE_MONITORING,
    CACHE_CIRCUIT_BREAKER
)
from .logging import setup_logging
from .rate_limit import (
    RATE_LIMIT,
    RATE_LIMIT_STRATEGY
)
from .permissions import (
    UserRole,
    Permission,
    ROLE_PERMISSIONS,
    ENDPOINT_PERMISSIONS,
    SUPER_ADMINS,
    ROLE_RATE_LIMITS
)
from .audit import (
    AuditLevel,
    AuditCategory,
    AUDIT_CONFIG,
    AUDIT_EVENTS
)
from .notification import (
    NotificationChannel,
    NotificationPriority,
    NotificationType,
    NOTIFICATION_TEMPLATES,
    CHANNEL_CONFIG,
    PRIORITY_SETTINGS
)
from .validation import (
    REGEX_PATTERNS,
    VALIDATION_RULES,
    validate_date_range,
    validate_product_metadata
)

# Create config object that combines all settings
class Config:
    def __init__(self):
        # API Version
        self.API_VERSION = API_VERSION  # Tambahkan ini ke dalam Config class
        
        # Load settings based on environment
        self.ENV = settings_config.ENV
        self.DEBUG = settings_config.DEBUG
        self.DATABASE_URL = settings_config.DATABASE_URL
        self.SECRET_KEY = settings_config.SECRET_KEY
        
        # Security settings
        self.JWT_SECRET_KEY = JWT_SECRET_KEY
        self.TOKEN_EXPIRATION_SECONDS = TOKEN_EXPIRATION_SECONDS
        self.PASSWORD_HASH_SCHEME = PASSWORD_HASH_SCHEME
        
        # Database settings
        self.DATABASE_POOL_SIZE = DATABASE_POOL_SIZE
        self.DATABASE_TIMEOUT = DATABASE_TIMEOUT
        
        # Cache settings
        self.CACHE_CONFIG = CACHE_CONFIG
        self.CACHE_TTL = CACHE_TTL
        self.CACHE_KEY_PATTERNS = CACHE_KEY_PATTERNS
        self.CACHE_INVALIDATION_RULES = CACHE_INVALIDATION_RULES
        self.CACHE_WARMING = CACHE_WARMING
        self.CACHE_MONITORING = CACHE_MONITORING
        self.CACHE_CIRCUIT_BREAKER = CACHE_CIRCUIT_BREAKER
        
        # Rate limiting
        self.RATE_LIMIT = RATE_LIMIT
        self.RATE_LIMIT_STRATEGY = RATE_LIMIT_STRATEGY
        
        # Permission settings
        self.ROLE_PERMISSIONS = ROLE_PERMISSIONS
        self.ENDPOINT_PERMISSIONS = ENDPOINT_PERMISSIONS
        self.SUPER_ADMINS = SUPER_ADMINS
        self.ROLE_RATE_LIMITS = ROLE_RATE_LIMITS
        
        # Audit settings
        self.AUDIT_CONFIG = AUDIT_CONFIG
        self.AUDIT_EVENTS = AUDIT_EVENTS
        
        # Notification settings
        self.NOTIFICATION_TEMPLATES = NOTIFICATION_TEMPLATES
        self.CHANNEL_CONFIG = CHANNEL_CONFIG
        self.PRIORITY_SETTINGS = PRIORITY_SETTINGS
        
        # Validation settings
        self.REGEX_PATTERNS = REGEX_PATTERNS
        self.VALIDATION_RULES = VALIDATION_RULES

        # Generate encryption key
        import base64
        import os
        self.ENCRYPTION_KEY = base64.urlsafe_b64encode(os.urandom(32))

# Create single config instance
config = Config()

# Setup logging
setup_logging()

# Export everything
__all__ = [
    'config',
    'API_VERSION',  # Tambahkan ini ke __all__
    'UserRole',
    'Permission', 
    'AuditLevel',
    'AuditCategory',
    'NotificationChannel',
    'NotificationPriority',
    'NotificationType',
    'validate_date_range',
    'validate_product_metadata',
]