from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EmotionRecord
from app.repositories.base_repo import BaseRepository

from collections import defaultdict


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

        # Добавить в конец класса EmotionRepository

        def get_weekday_averages(
                self,
                *,
                user_id: UUID,
                start_date: date,
                end_date: date,
        ) -> dict[int, dict[str, float]]:
            """
            Возвращает средние значения по дням недели.

            Returns:
                {
                    0: {"mood": 6.5, "anxiety": 5.2, "fatigue": 5.8, "count": 5},  # Monday
                    1: {"mood": 6.8, "anxiety": 4.9, "fatigue": 5.5, "count": 4},  # Tuesday
                    ...
                    6: {"mood": 7.2, "anxiety": 4.0, "fatigue": 4.8, "count": 3}   # Sunday
                }
            """
            from sqlalchemy import func

            records = self.list_by_user_and_period(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
            )

            if not records:
                return {}

            # Группируем по дням недели
            weekday_moods = defaultdict(list)
            weekday_anxieties = defaultdict(list)
            weekday_fatigues = defaultdict(list)

            for record in records:
                weekday = record.record_date.weekday()
                weekday_moods[weekday].append(float(record.mood))
                weekday_anxieties[weekday].append(float(record.anxiety))
                weekday_fatigues[weekday].append(float(record.fatigue))

            # Вычисляем средние
            result = {}
            for weekday in range(7):
                if weekday_moods.get(weekday):
                    result[weekday] = {
                        "mood": round(sum(weekday_moods[weekday]) / len(weekday_moods[weekday]), 1),
                        "anxiety": round(sum(weekday_anxieties[weekday]) / len(weekday_anxieties[weekday]), 1),
                        "fatigue": round(sum(weekday_fatigues[weekday]) / len(weekday_fatigues[weekday]), 1),
                        "count": len(weekday_moods[weekday]),
                    }
                else:
                    result[weekday] = {
                        "mood": 0.0,
                        "anxiety": 0.0,
                        "fatigue": 0.0,
                        "count": 0,
                    }

            return result

        def get_daily_averages(
                self,
                *,
                user_id: UUID,
                start_date: date,
                end_date: date,
        ) -> dict[date, dict[str, float]]:
            """
            Возвращает средние значения по каждому дню.
            """
            records = self.list_by_user_and_period(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
            )

            result = {}
            for record in records:
                result[record.record_date] = {
                    "mood": float(record.mood),
                    "anxiety": float(record.anxiety),
                    "fatigue": float(record.fatigue),
                }

            return result


# Backward-compatible alias for code that still imports the old repository name.
EmotionRecordRepository = EmotionRepository
