"""
Schemas for analytics endpoints.
"""

from typing import Dict

from pydantic import RootModel

from .common import BaseSchema


class LastMonthMetricsItem(BaseSchema):
    """Metrics for a single calendar day in the last-month analytics view."""

    mood: float
    anxiety: float
    fatigue: float


class LastMonthAnalyticsResponse(RootModel[Dict[str, LastMonthMetricsItem]]):
    """Mapping ``DD.MM.YYYY -> metrics`` for the last 30 tracked days."""

