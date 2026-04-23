"""
Сервис эмоций
"""
from datetime import date, datetime, timedelta
from uuid import UUID
from typing import Dict, Any, List, Optional
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.emotion_repo import EmotionRepository
from app.services.notification_service import NotificationService
from app.utils import (
    calculate_moving_average,
    categorize_trigger,
    detect_consecutive_threshold,
    validate_note_content,
)
from app.schemas.emotion import (
    EmotionRecordResponse,
    EmotionRecordWithStats,
    TodayRecordResponse,
    EmotionRecordList,
    MiniStats,
)


class EmotionService:
    """Сервис для работы с эмоциями"""

    def __init__(self, db: Session):
        """
        Инициализация сервиса эмоций

        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.repo = EmotionRepository(db)
        self.notif_service = NotificationService(db)

    def _calculate_mini_stats(self, user_id: UUID) -> Optional[MiniStats]:
        """Рассчитывает мини-статистику за последние 7 дней"""
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        records = self.repo.list_by_user_and_period(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        if not records:
            return None

        mood_values = [r.mood for r in records]
        anxiety_values = [r.anxiety for r in records]
        fatigue_values = [r.fatigue for r in records]
        window_size = len(records)

        avg_mood = calculate_moving_average(mood_values, window_size=window_size)[0]
        avg_anxiety = calculate_moving_average(anxiety_values, window_size=window_size)[0]
        avg_fatigue = calculate_moving_average(fatigue_values, window_size=window_size)[0]

        return MiniStats(
            last_7_days_avg={
                "mood": round(avg_mood, 1),
                "anxiety": round(avg_anxiety, 1),
                "fatigue": round(avg_fatigue, 1)
            }
        )

    def _to_response(self, record) -> EmotionRecordResponse:
        """Конвертирует ORM модель в Response схему"""
        return EmotionRecordResponse(
            id=record.id,
            user_id=record.user_id,
            mood=record.mood,
            anxiety=record.anxiety,
            fatigue=record.fatigue,
            sleep_hours=float(record.sleep_hours) if record.sleep_hours else None,
            note=record.note,
            record_date=record.record_date,
            created_at=record.created_at
        )

    @staticmethod
    def _detect_triggers(data: Dict[str, Any]) -> List[str]:
        """Эвристическое определение триггеров по метрикам и заметке."""
        triggers: List[str] = []
        mood = data.get("mood")
        anxiety = data.get("anxiety")
        fatigue = data.get("fatigue")
        sleep_hours = data.get("sleep_hours")
        note = (data.get("note") or "").lower()

        if isinstance(mood, int):
            mood_trigger = categorize_trigger(metric="intensity", value=mood)
            if mood_trigger == "low_intensity":
                triggers.append("low_mood")

        if isinstance(anxiety, int) and detect_consecutive_threshold(
            records=[{"anxiety": anxiety}],
            metric_name="anxiety",
            threshold=8,
            consecutive_days=1,
        ):
            triggers.append("high_anxiety")

        if isinstance(fatigue, int) and detect_consecutive_threshold(
            records=[{"fatigue": fatigue}],
            metric_name="fatigue",
            threshold=8,
            consecutive_days=1,
        ):
            triggers.append("high_fatigue")

        if sleep_hours is not None:
            sleep_trigger = categorize_trigger(metric="sleep_hours", value=int(sleep_hours))
            if sleep_trigger == "sleep_deprivation":
                triggers.append(sleep_trigger)

        return list(dict.fromkeys(triggers))

    def create_record(self, user_id: UUID, data: Dict[str, Any]) -> EmotionRecordWithStats:
        """
        Создание записи эмоции

        Args:
            user_id: ID пользователя
            data: Данные эмоции

        Returns:
            EmotionRecordWithStats: Объект с записью и статистикой
        """
        record_date = data.get("record_date", date.today())

        # Проверка на существующую запись за этот день
        existing = self.repo.get_by_user_and_date(user_id, record_date)
        if existing:
            raise ValueError("Record already exists for this date")

        sleep_hours = data.get("sleep_hours")
        if sleep_hours is not None:
            sleep_hours = Decimal(str(sleep_hours))

        note = data.get("note")
        if note is not None:
            note_validation = validate_note_content(note)
            if not note_validation["is_valid"]:
                raise ValueError(note_validation["error"])
            note = note_validation["sanitized"]

        record = self.repo.create(
            self.db,
            user_id=user_id,
            record_date=record_date,
            mood=data["mood"],
            anxiety=data["anxiety"],
            fatigue=data["fatigue"],
            sleep_hours=sleep_hours,
            note=note
        )

        mini_stats = self._calculate_mini_stats(user_id)
        triggers_detected = self._detect_triggers(data)

        return EmotionRecordWithStats(
            **self._to_response(record).model_dump(),
            mood_stats=mini_stats,
            triggers_detected=triggers_detected,
        )

    def get_today_record(self, user_id: UUID) -> TodayRecordResponse:
        """
        Получение записи эмоции за сегодня

        Args:
            user_id: ID пользователя

        Returns:
            TodayRecordResponse: Объект с записью за сегодня
        """
        record = self.repo.get_by_user_and_date(user_id, date.today())

        if record:
            return TodayRecordResponse(
                exists=True,
                record=self._to_response(record)
            )

        return TodayRecordResponse(exists=False, record=None)

    def get_history(
            self,
            user_id: UUID,
            start_date: date,
            end_date: date,
            limit: int
    ) -> List[EmotionRecordResponse]:
        """
        Получение истории эмоций за период

        Args:
            user_id: ID пользователя
            start_date: Начальная дата
            end_date: Конечная дата
            limit: Максимальное число записей

        Returns:
            list[EmotionRecordResponse]: Список записей эмоций
        """
        records = self.repo.get_by_user_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        return [self._to_response(r) for r in records]

    def update_record(
            self,
            user_id: UUID,
            record_id: UUID,
            data: Dict[str, Any]
    ) -> EmotionRecordResponse:
        """
        Обновление записи эмоции

        Args:
            user_id: ID пользователя
            record_id: ID записи
            data: Обновляемые данные

        Returns:
            EmotionRecordResponse: Обновленная запись
        """
        record = self.repo.get(record_id)

        if not record or record.user_id != user_id:
            raise ValueError("Record not found")

        update_data = {}
        if "mood" in data:
            update_data["mood"] = data["mood"]
        if "anxiety" in data:
            update_data["anxiety"] = data["anxiety"]
        if "fatigue" in data:
            update_data["fatigue"] = data["fatigue"]
        if "sleep_hours" in data:
            update_data["sleep_hours"] = Decimal(str(data["sleep_hours"])) if data["sleep_hours"] else None
        if "note" in data:
            note_validation = validate_note_content(data["note"])
            if not note_validation["is_valid"]:
                raise ValueError(note_validation["error"])
            update_data["note"] = note_validation["sanitized"]

        if update_data:
            record = self.repo.update(db_obj=record, obj_in=update_data)

        response = self._to_response(record)
        response.updated_at = datetime.utcnow()
        return response

    def delete_record(self, user_id: UUID, record_id: UUID) -> bool:
        """
        Удаление записи эмоции

        Args:
            user_id: ID пользователя
            record_id: ID записи

        Returns:
            bool: True если удалено успешно
        """
        record = self.repo.get(record_id)

        if not record or record.user_id != user_id:
            return False

        deleted = self.repo.remove(id=record_id)
        return deleted is not None