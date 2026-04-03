"""
Core Module

Infrastructure code, configuration, security, and shared utilities.
No business logic here - only foundational components.
"""

from .config import settings, Settings
from .database import engine, SessionLocal, Base, get_db
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    oauth2_scheme,
)
from .constants import (
    FREE_ANALYTICS_DAYS,
    PRO_ANALYTICS_DAYS,
    MAX_EXPORT_DAYS,
    MIN_CORRELATION_DAYS,
    FATIGUE_THRESHOLD,
    FATIGUE_CONSECUTIVE_DAYS,
    ANXIETY_THRESHOLD,
    ANXIETY_CONSECUTIVE_DAYS,
    MOOD_IMPROVEMENT_DELTA,
    MAX_NOTE_LENGTH,
    PASSWORD_MIN_LENGTH,
    REMINDER_ROTATION_DAYS,
    AUTONOMY_SUPPORTIVE_PREFIX,
)
from .exceptions import (
    AppException,
    SubscriptionRequiredException,
    InvalidPeriodException,
    InsufficientDataException,
    InvalidCredentialsException,
    ResourceNotFoundException,
)

__all__ = [
    "settings",
    "Settings",
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "verify_token",
    "oauth2_scheme",
    "FREE_ANALYTICS_DAYS",
    "PRO_ANALYTICS_DAYS",
    "MAX_EXPORT_DAYS",
    "MIN_CORRELATION_DAYS",
    "FATIGUE_THRESHOLD",
    "FATIGUE_CONSECUTIVE_DAYS",
    "ANXIETY_THRESHOLD",
    "ANXIETY_CONSECUTIVE_DAYS",
    "MOOD_IMPROVEMENT_DELTA",
    "MAX_NOTE_LENGTH",
    "PASSWORD_MIN_LENGTH",
    "REMINDER_ROTATION_DAYS",
    "AUTONOMY_SUPPORTIVE_PREFIX",
    "AppException",
    "SubscriptionRequiredException",
    "InvalidPeriodException",
    "InsufficientDataException",
    "InvalidCredentialsException",
    "ResourceNotFoundException",
]
