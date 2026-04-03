"""
Notification schemas - logs and preferences.

Used in:
- GET /api/v1/notifications
- PUT /api/v1/notifications/preferences
- POST /api/v1/notifications/test
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import Field

from .common import BaseSchema, UUIDMixin, NotificationChannel, DeliveryStatus


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class NotificationPreferencesUpdate(BaseSchema):
    """
    Update notification preferences.

    Used in: PUT /api/v1/notifications/preferences
    """
    channel: Optional[NotificationChannel] = None
    window_start: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    window_end: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly)$")
    reminders_enabled: Optional[bool] = None
    trend_alerts_enabled: Optional[bool] = None
    positive_feedback_enabled: Optional[bool] = None


class NotificationTestRequest(BaseSchema):
    """
    Test notification request.

    Used in: POST /api/v1/notifications/test
    """
    channel: NotificationChannel


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class NotificationLogResponse(UUIDMixin, BaseSchema):
    """
    Notification log entry.

    Used in: GET /api/v1/notifications
    """
    user_id: UUID
    recommendation_id: Optional[UUID] = None
    channel: NotificationChannel
    trigger_type: str
    message: str
    delivery_status: DeliveryStatus
    sent_at: datetime


class NotificationTestResponse(BaseSchema):
    """
    Test notification response.

    Used in: POST /api/v1/notifications/test
    """
    message: str
    channel: NotificationChannel
    sent_at: datetime


class NotificationList(BaseSchema):
    """
    List of notifications with pagination.

    Used in: GET /api/v1/notifications
    """
    items: List[NotificationLogResponse]
    total: int
