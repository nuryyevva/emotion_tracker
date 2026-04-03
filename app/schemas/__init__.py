"""
Schemas package - Pydantic models for API validation
"""

from .common import (
    NotificationChannel,
    SubscriptionPlan,
    SubscriptionStatus,
    DeliveryStatus,
    MetricType,
    ChartType,
    TriggerType,
    BaseSchema,
    TimestampMixin,
    UUIDMixin,
)
from .auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from .user import (
    UserResponse,
    UserUpdate,
    UserSettingsCreate,
    UserSettingsResponse,
    UserSettingsUpdate,
    HobbyCreate,
    HobbyResponse,
    CopingMethodCreate,
    CopingMethodResponse,
)
from .emotion import (
    EmotionRecordBase,
    EmotionRecordCreate,
    EmotionRecordUpdate,
    EmotionRecordResponse,
    EmotionRecordList,
    TodayRecordResponse,
)
from .notification import (
    NotificationLogResponse,
    NotificationPreferencesUpdate,
    NotificationTestRequest,
    NotificationTestResponse,
    NotificationList,
)
from .recommendation import (
    RecommendationTemplate,
    RecommendationList,
    RecommendationCreate,
)
from .health import HealthResponse, HealthServiceStatus

__all__ = [
    # Common
    "NotificationChannel",
    "SubscriptionPlan",
    "SubscriptionStatus",
    "DeliveryStatus",
    "MetricType",
    "ChartType",
    "TriggerType",
    "BaseSchema",
    "TimestampMixin",
    "UUIDMixin",
    # Auth
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    # User
    "UserResponse",
    "UserUpdate",
    "UserSettingsCreate",
    "UserSettingsResponse",
    "UserSettingsUpdate",
    "HobbyCreate",
    "HobbyResponse",
    "CopingMethodCreate",
    "CopingMethodResponse",
    # Emotion
    "EmotionRecordBase",
    "EmotionRecordCreate",
    "EmotionRecordUpdate",
    "EmotionRecordResponse",
    "EmotionRecordList",
    "TodayRecordResponse",
    # Notification
    "NotificationLogResponse",
    "NotificationPreferencesUpdate",
    "NotificationTestRequest",
    "NotificationTestResponse",
    "NotificationList",
    # Recommendation
    "RecommendationTemplate",
    "RecommendationList",
    "RecommendationCreate",
    # Health
    "HealthResponse",
    "HealthServiceStatus",
]
