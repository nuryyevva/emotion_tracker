from pydantic import Field, field_validator
from datetime import datetime
from uuid import UUID
from .common import BaseSchema, UUIDMixin, TimestampMixin, NotificationChannel

# --- Profile ---
class UserResponse(UUIDMixin, TimestampMixin):
    email: str
    timezone: str
    status: str

class UserSettingsCreate(BaseSchema):
    weekday_wake_up: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")  # HH:MM
    weekday_bedtime: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    weekend_wake_up: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    weekend_bedtime: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    notify_channel: NotificationChannel = NotificationChannel.EMAIL
    notify_window_start: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    notify_window_end: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    notify_frequency: str = Field(default="daily", description="daily, weekly")
    reminders_enabled: bool = True

class UserSettingsResponse(UserSettingsCreate, UUIDMixin):
    user_id: UUID
    updated_at: datetime

class UserSettingsUpdate(BaseSchema):
    weekday_wake_up: str | None = None
    weekday_bedtime: str | None = None
    weekend_wake_up: str | None = None
    weekend_bedtime: str | None = None
    notify_channel: NotificationChannel | None = None
    notify_window_start: str | None = None
    notify_window_end: str | None = None
    notify_frequency: str | None = None
    reminders_enabled: bool | None = None

# --- Hobbies & Coping ---
class HobbyCreate(BaseSchema):
    hobby: str = Field(..., min_length=2, max_length=50)

class HobbyResponse(HobbyCreate, UUIDMixin):
    user_id: UUID
    created_at: datetime

class CopingMethodCreate(BaseSchema):
    method: str = Field(..., min_length=2, max_length=100)

class CopingMethodResponse(CopingMethodCreate, UUIDMixin):
    user_id: UUID
    created_at: datetime
