"""
Analytics service for emotional data analysis.
"""
from datetime import date, datetime, timedelta
from uuid import UUID
from typing import Dict, List, Any, Optional
from collections import defaultdict

from sqlalchemy.orm import Session

from app.repositories.emotion_repo import EmotionRepository
from app.schemas.analytics import (
    WeeklyAveragesResponse,
    DailyAverageResponse,
    WeekdayAverageResponse,
    WeekdayAveragesListResponse,
)


class AnalyticsService:
    """Service for analytics and statistics."""

    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    WEEKDAYS_RU = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    def __init__(self, db: Session):
        """Initialize analytics service."""
        self.db = db
        self.emotion_repo = EmotionRepository(db)

    def get_daily_averages(
            self,
            user_id: UUID,
            start_date: date,
            end_date: date,
    ) -> WeeklyAveragesResponse:
        """
        Get daily average values for emotions over a period.

        Args:
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            WeeklyAveragesResponse with daily averages in format:
            {"DD.MM.YYYY": {"mood": float, "anxiety": float, "fatigue": float}}
        """
        # Get all records in period
        records = self.emotion_repo.list_by_user_and_period(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Build dictionary of records by date
        records_by_date: Dict[date, Dict[str, float]] = {}
        for record in records:
            records_by_date[record.record_date] = {
                "mood": float(record.mood),
                "anxiety": float(record.anxiety),
                "fatigue": float(record.fatigue),
            }

        # Build response with all dates in period
        result_data: Dict[str, DailyAverageResponse] = {}
        current_date = start_date
        days_with_data = 0

        while current_date <= end_date:
            formatted_date = current_date.strftime("%d.%m.%Y")

            if current_date in records_by_date:
                days_with_data += 1
                data = records_by_date[current_date]
                result_data[formatted_date] = DailyAverageResponse(
                    mood=round(data["mood"], 1),
                    anxiety=round(data["anxiety"], 1),
                    fatigue=round(data["fatigue"], 1),
                )
            else:
                # Return None or empty values for days without data
                result_data[formatted_date] = DailyAverageResponse(
                    mood=0.0,
                    anxiety=0.0,
                    fatigue=0.0,
                )

            current_date += timedelta(days=1)

        total_days = (end_date - start_date).days + 1

        return WeeklyAveragesResponse(
            data=result_data,
            period_start=start_date,
            period_end=end_date,
            total_days=total_days,
            days_with_data=days_with_data,
        )

    def get_weekday_averages(
            self,
            user_id: UUID,
            start_date: date,
            end_date: date,
    ) -> WeekdayAveragesListResponse:
        """
        Get average emotion values grouped by day of week.

        Args:
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            WeekdayAveragesListResponse with averages for each weekday
        """
        # Get all records in period
        records = self.emotion_repo.list_by_user_and_period(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Group by weekday (0 = Monday, 6 = Sunday)
        weekday_moods: Dict[int, List[float]] = defaultdict(list)
        weekday_anxieties: Dict[int, List[float]] = defaultdict(list)
        weekday_fatigues: Dict[int, List[float]] = defaultdict(list)

        for record in records:
            # Python's weekday(): Monday=0, Sunday=6
            weekday = record.record_date.weekday()

            weekday_moods[weekday].append(float(record.mood))
            weekday_anxieties[weekday].append(float(record.anxiety))
            weekday_fatigues[weekday].append(float(record.fatigue))

        # Build response for each weekday
        items = []
        for i, weekday_name in enumerate(self.WEEKDAYS):
            if weekday_moods.get(i):
                avg_mood = sum(weekday_moods[i]) / len(weekday_moods[i])
                avg_anxiety = sum(weekday_anxieties[i]) / len(weekday_anxieties[i])
                avg_fatigue = sum(weekday_fatigues[i]) / len(weekday_fatigues[i])
                sample_count = len(weekday_moods[i])
            else:
                avg_mood = 0.0
                avg_anxiety = 0.0
                avg_fatigue = 0.0
                sample_count = 0

            items.append(
                WeekdayAverageResponse(
                    weekday=weekday_name,
                    mood=round(avg_mood, 1),
                    anxiety=round(avg_anxiety, 1),
                    fatigue=round(avg_fatigue, 1),
                    sample_count=sample_count,
                )
            )

        return WeekdayAveragesListResponse(
            items=items,
            period_start=start_date,
            period_end=end_date,
        )