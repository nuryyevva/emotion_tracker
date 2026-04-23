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
    BOTH = "both"


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    PRO = "pro"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"
    TRIAL = "trial"


class DeliveryStatus(str, Enum):
    """Notification delivery status."""
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


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



class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"


class NotifyFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SMART = "smart"


def enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]

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
