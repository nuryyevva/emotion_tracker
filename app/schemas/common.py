from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime
from uuid import UUID

class BaseSchema(BaseModel):
    """Базовая схема с настройками"""
    model_config = ConfigDict(from_attributes=True)

class NotificationChannel(str, Enum):
    EMAIL = "email"
    TELEGRAM = "telegram"

class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class MetricType(str, Enum):
    MOOD = "mood"
    ANXIETY = "anxiety"
    FATIGUE = "fatigue"

class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    HEATMAP = "heatmap"

# Общие поля
class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime | None = None

class UUIDMixin(BaseModel):
    id: UUID
