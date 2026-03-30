from pydantic import Field
from datetime import datetime
from uuid import UUID
from .common import BaseSchema, UUIDMixin, NotificationChannel, DeliveryStatus

class RecommendationTemplate(BaseSchema):
    id: UUID
    trigger_type: str  # e.g., "fatigue_high", "anxiety_high"
    category: str
    message: str
    priority: int
    is_active: bool

class NotificationLogResponse(UUIDMixin, BaseSchema):
    user_id: UUID
    recommendation_id: UUID | None
    channel: NotificationChannel
    trigger_type: str
    message: str
    delivery_status: DeliveryStatus
    sent_at: datetime

class NotificationCreate(BaseSchema):
    user_id: UUID
    channel: NotificationChannel
    trigger_type: str
    message: str
    recommendation_id: UUID | None = None
