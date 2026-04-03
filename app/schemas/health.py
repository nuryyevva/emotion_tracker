"""
Health check schemas.

Used in:
- GET /api/v1/health
"""

from datetime import datetime
from typing import Dict, Optional

from .common import BaseSchema


class HealthServiceStatus(BaseSchema):
    """Status of a single service."""
    status: str  # "connected", "operational", "disconnected"
    response_time_ms: Optional[int] = None


class HealthResponse(BaseSchema):
    """
    Health check response.

    Used in: GET /api/v1/health
    """
    status: str = "healthy"
    version: str
    timestamp: datetime
    services: Dict[str, HealthServiceStatus]
