"""
User profile and settings schemas.

Used in:
- GET/PUT/DELETE /api/v1/users/me
- GET/PUT /api/v1/users/me/settings
- POST/DELETE /api/v1/users/me/settings/hobbies
- POST/DELETE /api/v1/users/me/settings/coping-methods
"""

from datetime import datetime, time
from typing import Optional, List
from uuid import UUID
from pydantic import Field, field_validator, ConfigDict

from .common import BaseSchema, UUIDMixin, NotificationChannel


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class UserUpdate(BaseSchema):
    """
    User profile update request.

    Used in: PUT /api/v1/users/me
    """
    timezone: Optional[str] = Field(
        default=None,
        description="IANA timezone"
    )


class UserSettingsCreate(BaseSchema):
    """
    User settings creation (internal use during registration).
    """
    weekday_wake_up: time
    weekday_bedtime: time
    weekend_wake_up: time
    weekend_bedtime: time
    notify_channel: NotificationChannel = NotificationChannel.EMAIL
    notify_window_start: time
    notify_window_end: time
    notify_frequency: str = Field(default="daily", pattern="^(daily|weekly)$")
    reminders_enabled: bool = True


class UserSettingsUpdate(BaseSchema):
    """
    User settings partial update.

    Used in: PUT /api/v1/users/me/settings
    """
    weekday_wake_up: Optional[time] = None
    weekday_bedtime: Optional[time] = None
    weekend_wake_up: Optional[time] = None
    weekend_bedtime: Optional[time] = None
    notify_channel: Optional[NotificationChannel] = None
    notify_window_start: Optional[time] = None
    notify_window_end: Optional[time] = None
    notify_frequency: Optional[str] = Field(None, pattern="^(daily|weekly)$")
    reminders_enabled: Optional[bool] = None

    @field_validator('notify_window_end')
    @classmethod
    def validate_window(cls, v: Optional[time], info) -> Optional[time]:
        """Validate that window end is after start."""
        if v is None:
            return v

        # Get start time from values or data
        start = info.data.get('notify_window_start')
        if start and v <= start:
            raise ValueError("Notification window end must be after start")
        return v


class HobbyCreate(BaseSchema):
    """
    Hobby creation request.

    Used in: POST /api/v1/users/me/settings/hobbies
    """
    hobby: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Hobby name or tag"
    )


class CopingMethodCreate(BaseSchema):
    """
    Coping method creation request.

    Used in: POST /api/v1/users/me/settings/coping-methods
    """
    method: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Stress coping method description"
    )


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class UserResponse(UUIDMixin, BaseSchema):
    """
    User profile response.

    Used in: GET /api/v1/users/me
    """
    email: str
    timezone: str
    status: str
    created_at: datetime
    updated_at: datetime


class UserSettingsResponse(BaseSchema):
    """
    User settings response.

    Used in: GET /api/v1/users/me/settings, PUT /api/v1/users/me/settings
    """
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    weekday_wake_up: time
    weekday_bedtime: time
    weekend_wake_up: time
    weekend_bedtime: time
    notify_channel: NotificationChannel
    notify_window_start: time
    notify_window_end: time
    notify_frequency: str
    reminders_enabled: bool
    updated_at: datetime
    hobbies: List[str] = []
    coping_methods: List[str] = []


class HobbyResponse(UUIDMixin, BaseSchema):
    """
    Hobby response.

    Used in: POST /api/v1/users/me/settings/hobbies
    """
    user_id: UUID
    hobby: str
    created_at: datetime


class CopingMethodResponse(UUIDMixin, BaseSchema):
    """
    Coping method response.

    Used in: POST /api/v1/users/me/settings/coping-methods
    """
    user_id: UUID
    method: str
    created_at: datetime


class MessageResponse(BaseSchema):
    """Generic message response."""
    message: str
