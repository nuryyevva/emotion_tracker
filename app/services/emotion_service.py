"""
Сервис эмоций
"""
from datetime import date, datetime
from uuid import UUID
from typing import Dict, Any, List, Optional
from decimal import Decimal

from sqlalchemy.orm import Session

from ..repositories.emotion_repo import EmotionRepository
from ..services.notification_service import NotificationService
from ..schemas.emotion import (
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
        self.repo = EmotionRepository()
        self.notif_service = NotificationService(db)

    def _calculate_mini_stats(self, user_id: UUID) -> Optional[MiniStats]:
        """Рассчитывает мини-статистику за последние 7 дней"""
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        records = self.repo.list_by_user_and_period(
            self.db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        if not records:
            return None

        avg_mood = sum(r.mood for r in records) / len(records)
        avg_anxiety = sum(r.anxiety for r in records) / len(records)
        avg_fatigue = sum(r.fatigue for r in records) / len(records)

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
        existing = self.repo.get_by_user_and_date(self.db, user_id, record_date)
        if existing:
            raise ValueError("Record already exists for this date")

        sleep_hours = data.get("sleep_hours")
        if sleep_hours is not None:
            sleep_hours = Decimal(str(sleep_hours))

        record = self.repo.create(
            self.db,
            user_id=user_id,
            record_date=record_date,
            mood=data["mood"],
            anxiety=data["anxiety"],
            fatigue=data["fatigue"],
            sleep_hours=sleep_hours,
            note=data.get("note")
        )

        mini_stats = self._calculate_mini_stats(user_id)

        return EmotionRecordWithStats(
            **self._to_response(record).model_dump(),
            mini_stats=mini_stats
        )

    def get_today_record(self, user_id: UUID) -> TodayRecordResponse:
        """
        Получение записи эмоции за сегодня

        Args:
            user_id: ID пользователя

        Returns:
            TodayRecordResponse: Объект с записью за сегодня
        """
        record = self.repo.get_by_user_and_date(self.db, user_id, date.today())

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
            end_date: date
    ) -> List[EmotionRecordResponse]:
        """
        Получение истории эмоций за период

        Args:
            user_id: ID пользователя
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            list[EmotionRecordResponse]: Список записей эмоций
        """
        records = self.repo.list_by_user_and_period(
            self.db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
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
        record = self.repo.get(self.db, record_id)

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
            update_data["note"] = data["note"]

        if update_data:
            record = self.repo.update(self.db, db_obj=record, obj_in=update_data)

        return self._to_response(record)

    def delete_record(self, user_id: UUID, record_id: UUID) -> bool:
        """
        Удаление записи эмоции

        Args:
            user_id: ID пользователя
            record_id: ID записи

        Returns:
            bool: True если удалено успешно
        """
        record = self.repo.get(self.db, record_id)

        if not record or record.user_id != user_id:
            return False

        deleted = self.repo.remove(self.db, id=record_id)
        return deleted is not None


from datetime import timedelta