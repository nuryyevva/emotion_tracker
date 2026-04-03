"""
Emotion record schemas - daily check-ins.

Used in:
- POST /api/v1/emotions
- GET /api/v1/emotions/today
- GET /api/v1/emotions
- PUT /api/v1/emotions/{id}
- DELETE /api/v1/emotions/{id}
"""

from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import Field

from .common import BaseSchema, UUIDMixin
# from .analytics import TrendInsight


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class EmotionRecordBase(BaseSchema):
    """Base emotion record schema with validation."""
    mood: int = Field(
        ...,
        ge=1,
        le=10,
        description="Mood score (1-10 scale)"
    )
    anxiety: int = Field(
        ...,
        ge=1,
        le=10,
        description="Anxiety level (1-10 scale)"
    )
    fatigue: int = Field(
        ...,
        ge=1,
        le=10,
        description="Fatigue level (1-10 scale)"
    )
    sleep_hours: Optional[float] = Field(
        default=None,
        ge=0,
        le=24,
        description="Actual sleep duration in hours (0-24)"
    )
    note: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional text note (max 500 characters)"
    )
    record_date: date = Field(
        default_factory=date.today,
        description="Date of the record (defaults to today)"
    )


class EmotionRecordCreate(EmotionRecordBase):
    """
    Create emotion record request.

    Used in: POST /api/v1/emotions
    """
    pass


class EmotionRecordUpdate(BaseSchema):
    """
    Partial update of emotion record.

    Used in: PUT /api/v1/emotions/{id}
    """
    mood: Optional[int] = Field(None, ge=1, le=10)
    anxiety: Optional[int] = Field(None, ge=1, le=10)
    fatigue: Optional[int] = Field(None, ge=1, le=10)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    note: Optional[str] = Field(None, max_length=500)


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class EmotionRecordResponse(UUIDMixin, BaseSchema):
    """
    Emotion record response.

    Used in: POST/GET/PUT /api/v1/emotions
    """
    user_id: UUID
    mood: int
    anxiety: int
    fatigue: int
    sleep_hours: Optional[float]
    note: Optional[str]
    record_date: date
    created_at: datetime
    updated_at: datetime


class MiniStats(BaseSchema):
    """Mini statistics for last 7 days."""
    last_7_days_avg: dict[str, float]


class EmotionRecordWithStats(EmotionRecordResponse):
    """Emotion record with mini statistics and triggers."""
    mini_stats: Optional[MiniStats] = None
    # triggers_detected: Optional[List[TrendInsight]] = None


class TodayRecordResponse(BaseSchema):
    """
    Check if today's record exists.

    Used in: GET /api/v1/emotions/today
    """
    exists: bool
    record: Optional[EmotionRecordResponse] = None


class EmotionRecordList(BaseSchema):
    """
    List of emotion records with pagination.

    Used in: GET /api/v1/emotions
    """
    items: List[EmotionRecordResponse]
    total: int
    period: dict[str, date]
