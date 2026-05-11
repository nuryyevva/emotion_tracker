"""
Analytics schemas for emotional data analysis.
"""

from datetime import date
from typing import Dict, List, Optional
from pydantic import Field

from .common import BaseSchema

# =============================================================================
# AVERAGE ANALYTICS
# =============================================================================


class DailyAverageResponse(BaseSchema):
    """Response for daily average values."""
    mood: float = Field(..., description="Average mood score")
    anxiety: float = Field(..., description="Average anxiety level")
    fatigue: float = Field(..., description="Average fatigue level")


class WeeklyAveragesResponse(BaseSchema):
    """Response for weekly averages by weekday."""
    data: Dict[str, DailyAverageResponse] = Field(
        ...,
        description="Dictionary with dates as keys and daily averages as values"
    )
    period_start: date = Field(..., description="Start date of the period")
    period_end: date = Field(..., description="End date of the period")
    total_days: int = Field(..., description="Total number of days in period")
    days_with_data: int = Field(..., description="Number of days with emotion records")


class WeekdayAverageResponse(BaseSchema):
    """Response for average values by day of week."""
    weekday: str = Field(..., description="Day of week (Monday, Tuesday, etc.)")
    mood: float = Field(..., description="Average mood for this weekday")
    anxiety: float = Field(..., description="Average anxiety for this weekday")
    fatigue: float = Field(..., description="Average fatigue for this weekday")
    sample_count: int = Field(..., description="Number of records used for calculation")


class WeekdayAveragesListResponse(BaseSchema):
    """Response for list of weekday averages."""
    items: List[WeekdayAverageResponse] = Field(..., description="List of weekday averages")
    period_start: date = Field(..., description="Start date of the period")
    period_end: date = Field(..., description="End date of the period")