"""
Service layer for analytics endpoints.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.emotion_repo import EmotionRepository
from app.schemas.analytics import LastMonthAnalyticsResponse, LastMonthMetricsItem


class AnalyticsService:
    """Provides analytics data in API-ready formats."""

    def __init__(self, db: Session):
        self.db = db
        self.emotion_repo = EmotionRepository(db)

    def get_last_month(self, user_id: UUID) -> LastMonthAnalyticsResponse:
        """Build the ``/analytics/last-month`` response for the current user.

        The API contract expects a flat JSON object where each key is a date in
        ``DD.MM.YYYY`` format and each value contains three numeric metrics.
        Because the database stores at most one record per user per day, each
        date maps directly to one emotion record.
        """

        records = self.emotion_repo.get_last_month_metrics(user_id=user_id)
        payload = {
            record.record_date.strftime("%d.%m.%Y"): LastMonthMetricsItem(
                mood=float(record.mood),
                anxiety=float(record.anxiety),
                fatigue=float(record.fatigue),
            )
            for record in records
        }
        return LastMonthAnalyticsResponse(payload)

