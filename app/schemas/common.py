"""
Common schemas, enums, and mixins used across the application.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# =============================================================================
# ENUMS
# =============================================================================


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    TELEGRAM = "telegram"


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    PRO = "pro"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class DeliveryStatus(str, Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class MetricType(str, Enum):
    """Emotion metrics that can be tracked."""
    MOOD = "mood"
    ANXIETY = "anxiety"
    FATIGUE = "fatigue"


class ChartType(str, Enum):
    """Chart visualization types."""
    LINE = "line"
    BAR = "bar"
    HEATMAP = "heatmap"


class TriggerType(str, Enum):
    """Notification trigger types based on System Analysis."""
    FATIGUE_HIGH = "fatigue_high"
    ANXIETY_HIGH = "anxiety_high"
    MOOD_LOW = "mood_low"
    MOOD_IMPROVEMENT = "mood_improvement"
    SLEEP_DEVIATION = "sleep_deviation"


# =============================================================================
# BASE SCHEMAS & MIXINS
# =============================================================================


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )


class UUIDMixin(BaseModel):
    """Mixin for UUID identification."""
    id: UUID


class TimestampMixin(BaseModel):
    """Mixin for created/updated timestamps."""
    created_at: datetime
    updated_at: datetime | None = None
