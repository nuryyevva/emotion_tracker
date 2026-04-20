"""
Сервис уведомлений
"""
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from ..repositories.notification_repo import NotificationRepository
from ..services.recommendation_service import RecommendationService
from ..services.user_service import UserService
from ..schemas.notification import NotificationLogResponse, NotificationList
from ..models import DeliveryStatus, NotificationLog


# Заглушка для Telegram клиента
class TelegramProvider:
    def send_message(self, chat_id: str, message: str) -> bool:
        return True


class NotificationService:
    """Сервис для работы с уведомлениями"""

    def __init__(self, db: Session):
        """
        Инициализация сервиса уведомлений

        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.repo = NotificationRepository()
        self.rec_service = RecommendationService(db)
        self.user_service = UserService(db)
        self.telegram_client = TelegramProvider()

    def _to_response(self, notification: NotificationLog) -> NotificationLogResponse:
        """Конвертирует ORM модель в Response схему"""
        return NotificationLogResponse(
            id=notification.id,
            user_id=notification.user_id,
            recommendation_id=notification.recommendation_id,
            channel=notification.channel,
            trigger_type=notification.trigger_type,
            message=notification.message,
            delivery_status=notification.delivery_status,
            sent_at=notification.sent_at
        )

    def send_trend_alert(self, user_id: UUID, trigger_type: str) -> None:
        """
        Отправка алерта об изменении тренда

        Args:
            user_id: ID пользователя
            trigger_type: Тип триггера
        """
        # Получение рекомендации
        recommendation = self.rec_service.get_recommendation(user_id, trigger_type)

        if not recommendation:
            return

        # Получение настроек пользователя
        settings = self.user_service.get_settings(user_id)

        # Создание лога уведомления
        notification = self.repo.create_log(
            self.db,
            user_id=user_id,
            recommendation_id=recommendation.get("id"),
            channel=settings.notify_channel.value if hasattr(settings.notify_channel, 'value') else str(
                settings.notify_channel),
            trigger_type=trigger_type,
            message=recommendation.get("message", "")
        )

        # Отправка через выбранный канал
        if settings.notify_channel.value == "telegram":
            # Получение telegram_chat_id пользователя
            user = self.user_service.get_profile(user_id)
            # В реальном проекте нужно получить chat_id из профиля
            # self.telegram_client.send_message(chat_id, notification.message)
            pass
        elif settings.notify_channel.value == "email":
            # Отправка email
            pass

        # Отметка об успешной отправке
        self.repo.mark_as_sent(self.db, notification=notification)

    def send_daily_reminder(self, user_id: UUID) -> None:
        """
        Отправка ежедневного напоминания

        Args:
            user_id: ID пользователя
        """
        settings = self.user_service.get_settings(user_id)

        if not settings.reminders_enabled:
            return

        reminder_message = "Как вы себя чувствуете сегодня? Не забудьте отметить свои эмоции!"

        notification = self.repo.create_log(
            self.db,
            user_id=user_id,
            recommendation_id=None,
            channel=settings.notify_channel.value if hasattr(settings.notify_channel, 'value') else str(
                settings.notify_channel),
            trigger_type="daily_reminder",
            message=reminder_message
        )

        # Отправка через выбранный канал
        if settings.notify_channel.value == "telegram":
            pass
        elif settings.notify_channel.value == "email":
            pass

        self.repo.mark_as_sent(self.db, notification=notification)

    def get_history(self, user_id: UUID, limit: int = 50) -> NotificationList:
        """
        Получение истории уведомлений

        Args:
            user_id: ID пользователя
            limit: Лимит уведомлений

        Returns:
            NotificationList: Список уведомлений
        """
        notifications = self.repo.get_by_user(self.db, user_id=user_id)

        # Ограничение по лимиту
        notifications = notifications[:limit]

        return NotificationList(
            items=[self._to_response(n) for n in notifications],
            total=len(notifications)
        )