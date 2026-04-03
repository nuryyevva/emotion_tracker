"""
Recommendation schemas - bank of recommendations.

Used in:
- GET /api/v1/recommendations
- POST /api/v1/recommendations (Admin)
"""

from datetime import datetime
from typing import Optional, List
from pydantic import Field

from .common import BaseSchema, UUIDMixin


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class RecommendationCreate(BaseSchema):
    """
    Create recommendation request (Admin only).

    Used in: POST /api/v1/recommendations
    """
    trigger_type: str = Field(
        ...,
        description="Trigger type (e.g., 'fatigue_high', 'anxiety_high')"
    )
    category: str = Field(
        ...,
        description="Category (e.g., 'breathing', 'micro-break', 'social')"
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Recommendation text"
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Priority level (1-10, higher = more important)"
    )


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class RecommendationTemplate(UUIDMixin, BaseSchema):
    """
    Recommendation template response.

    Used in: GET /api/v1/recommendations
    """
    trigger_type: str
    category: str
    message: str
    priority: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RecommendationList(BaseSchema):
    """
    List of recommendations.

    Used in: GET /api/v1/recommendations
    """
    items: List[RecommendationTemplate]
    total: int
