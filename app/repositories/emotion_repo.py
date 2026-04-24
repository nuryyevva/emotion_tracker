from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EmotionRecord
from app.repositories.base_repo import BaseRepository


class EmotionRepository(BaseRepository[EmotionRecord]):
    """Repository for daily emotion check-ins and emotion-based analytics."""

    def __init__(self, db: Session):
        super().__init__(db)

    model = EmotionRecord

    def get_by_user_and_date(self, user_id: UUID, record_date: date) -> EmotionRecord | None:
        """Return the emotion record for a specific user and day."""

        stmt = select(EmotionRecord).where(
            EmotionRecord.user_id == user_id,
            EmotionRecord.record_date == record_date,
        )
        return self.db.scalar(stmt)

    def list_by_user(self, user_id: UUID) -> list[EmotionRecord]:
        """Return all emotion records of a user ordered from newest to oldest."""

        stmt = (
            select(EmotionRecord)
            .where(EmotionRecord.user_id == user_id)
            .order_by(EmotionRecord.record_date.desc())
        )
        return list(self.db.scalars(stmt))

    def list_by_user_and_period(
        self,
        *,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[EmotionRecord]:
        """Return all records within the inclusive date range in chronological order."""

        stmt = (
            select(EmotionRecord)
            .where(
                EmotionRecord.user_id == user_id,
                EmotionRecord.record_date >= start_date,
                EmotionRecord.record_date <= end_date,
            )
            .order_by(EmotionRecord.record_date.asc())
        )
        return list(self.db.scalars(stmt))

    def get_by_user_date_range(
        self,
        *,
        user_id: UUID,
        start_date: date,
        end_date: date,
        limit: int | None = None,
    ) -> list[EmotionRecord]:
        """Architecture-oriented date range query with optional limit.

        Unlike ``list_by_user_and_period``, this method returns the newest records
        first because it is designed for history views and service-layer filters.
        """

        stmt = (
            select(EmotionRecord)
            .where(
                EmotionRecord.user_id == user_id,
                EmotionRecord.record_date >= start_date,
                EmotionRecord.record_date <= end_date,
            )
            .order_by(EmotionRecord.record_date.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.db.scalars(stmt))

    def get_latest(self, *, user_id: UUID, days: int = 7) -> list[EmotionRecord]:
        """Return the most recent ``days`` records for quick widgets and summaries.

        Note:
            Here ``days`` is currently interpreted as the number of latest
            records, not as a strict calendar interval. If a user has gaps in
            tracking, the method still returns up to N latest entries.
        """

        records = self.list_by_user(user_id)
        return records[:days]


# Backward-compatible alias for code that still imports the old repository name.
EmotionRecordRepository = EmotionRepository
