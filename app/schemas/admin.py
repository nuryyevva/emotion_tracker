"""
Admin schemas for managing all entities in the system.
"""
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import Field

from .common import BaseSchema, UUIDMixin, UserStatus, NotificationChannel, DeliveryStatus, SubscriptionStatus


# =============================================================================
# USER SCHEMAS
# =============================================================================

class AdminUserResponse(UUIDMixin, BaseSchema):
    """Full user response for admin panel."""
    email: str
    password_hash: str
    timezone: str
    telegram_chat_id: Optional[str] = None
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class AdminUserList(BaseSchema):
    """List of users for admin panel."""
    items: List[AdminUserResponse]
    total: int


# =============================================================================
# USER SETTINGS SCHEMAS
# =============================================================================

class AdminUserSettingsResponse(UUIDMixin, BaseSchema):
    """Full user settings response for admin panel."""
    model_config = BaseSchema.model_config.copy()
    model_config['from_attributes'] = True
    
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


class AdminUserSettingsList(BaseSchema):
    """List of user settings for admin panel."""
    items: List[AdminUserSettingsResponse]
    total: int


# =============================================================================
# USER HOBBIES SCHEMAS
# =============================================================================

class AdminHobbyResponse(UUIDMixin, BaseSchema):
    """Full hobby response for admin panel."""
    user_id: UUID
    hobby: str
    created_at: datetime


class AdminHobbyList(BaseSchema):
    """List of hobbies for admin panel."""
    items: List[AdminHobbyResponse]
    total: int


# =============================================================================
# USER COPING METHODS SCHEMAS
# =============================================================================

class AdminCopingMethodResponse(UUIDMixin, BaseSchema):
    """Full coping method response for admin panel."""
    user_id: UUID
    method: str
    created_at: datetime


class AdminCopingMethodList(BaseSchema):
    """List of coping methods for admin panel."""
    items: List[AdminCopingMethodResponse]
    total: int


# =============================================================================
# EMOTION RECORDS SCHEMAS
# =============================================================================

class AdminEmotionRecordResponse(UUIDMixin, BaseSchema):
    """Full emotion record response for admin panel."""
    user_id: UUID
    record_date: date
    mood: int
    anxiety: int
    fatigue: int
    sleep_hours: Optional[Decimal] = None
    note: Optional[str] = None
    created_at: datetime


class AdminEmotionRecordList(BaseSchema):
    """List of emotion records for admin panel."""
    items: List[AdminEmotionRecordResponse]
    total: int


# =============================================================================
# NOTIFICATION LOG SCHEMAS
# =============================================================================

class AdminNotificationLogResponse(UUIDMixin, BaseSchema):
    """Full notification log response for admin panel."""
    user_id: UUID
    recommendation_id: Optional[UUID] = None
    channel: str
    trigger_type: str
    message: str
    delivery_status: DeliveryStatus
    sent_at: datetime


class AdminNotificationLogList(BaseSchema):
    """List of notification logs for admin panel."""
    items: List[AdminNotificationLogResponse]
    total: int


# =============================================================================
# RECOMMENDATION SCHEMAS
# =============================================================================

class AdminRecommendationCreate(BaseSchema):
    """Create recommendation request for admin panel."""
    trigger_type: str = Field(..., description="Trigger type (e.g., 'fatigue_high', 'anxiety_high')")
    category: str = Field(..., description="Category (e.g., 'breathing', 'micro-break', 'social')")
    message: str = Field(..., min_length=10, max_length=500, description="Recommendation text")
    priority: int = Field(default=5, ge=1, le=10, description="Priority level (1-10)")
    is_active: bool = Field(default=True, description="Whether the recommendation is active")


class AdminRecommendationResponse(UUIDMixin, BaseSchema):
    """Full recommendation response for admin panel."""
    trigger_type: str
    category: str
    message: str
    priority: int
    is_active: bool


class AdminRecommendationList(BaseSchema):
    """List of recommendations for admin panel."""
    items: List[AdminRecommendationResponse]
    total: int


# =============================================================================
# SUBSCRIPTION SCHEMAS
# =============================================================================

class AdminSubscriptionResponse(UUIDMixin, BaseSchema):
    """Full subscription response for admin panel."""
    user_id: UUID
    plan: str
    status: SubscriptionStatus
    started_at: datetime
    expires_at: Optional[datetime] = None
    provider: Optional[str] = None
    external_payment_id: Optional[str] = None


class AdminSubscriptionList(BaseSchema):
    """List of subscriptions for admin panel."""
    items: List[AdminSubscriptionResponse]
    total: int
