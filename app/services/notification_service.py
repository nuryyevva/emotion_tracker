"""
Сервис уведомлений
"""
from uuid import UUID

from sqlalchemy.orm import Session

from ..repositories.notification_repo import NotificationRepository
from ..services.recommendation_service import RecommendationService
from ..services.user_service import UserService
from ..schemas.notification import NotificationLogResponse, NotificationList
from app.utils import is_within_notification_window
from app.core.constants import REMINDER_ROTATION_DAYS
from app.core.clients.telegram_client import TelegramProvider

class NotificationService:
    """Сервис для работы с уведомлениями"""

    def __init__(self, db: Session):
        """
        Инициализация сервиса уведомлений

        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.repo = NotificationRepository(db)
        self.rec_service = RecommendationService(db)
        self.user_service = UserService(db)
        self.telegram_client = TelegramProvider()

    def send_trend_alert(self, user_id: UUID, trigger_type: str) -> None:
        """
        Отправка алерта об изменении тренда

        Args:
            user_id: ID пользователя
            trigger_type: Тип триггера
        """
        # Check rotation
        recent = self.repo.get_recent_by_trigger(user_id=user_id, trigger_type=trigger_type,
                                                 days=REMINDER_ROTATION_DAYS)
        if recent:
            return  # Already sent recently

        # Get recommendation
        rec = self.rec_service.get_recommendation(user_id, trigger_type)
        if not rec:
            return

        # Get user settings
        settings = self.user_service.get_settings(user_id)

        # Send via preferred channel
        # success = False
        # Need chat_id from user profile (simplified here)
        success = self.telegram_client.send_trend_notification("chat_id_mock", trigger_type, rec.message)

        # Log
        log = self.repo.create_log(
            user_id=user_id,
            recommendation_id=rec.id,
            channel=settings.notify_channel,
            trigger_type=trigger_type,
            message=rec.message,
        )
        if success:
            self.repo.mark_as_sent(notification=log)
        else:
            self.repo.mark_as_failed(notification=log)

    def send_daily_reminder(self, user_id: UUID) -> None:
        """
        Отправка ежедневного напоминания

        Args:
            user_id: ID пользователя
        """
        settings = self.user_service.get_settings(user_id)
        if not settings.reminders_enabled:
            return

        # Check window
        if not is_within_notification_window(
                settings.notify_window_start.strftime("%H:%M"),
                settings.notify_window_end.strftime("%H:%M"),
                settings.,  # add timezone correctly
        ):
            return

        message = "Хотите отметить, как прошёл день? Это займёт 30 секунд."

        # Send
        self.telegram_client.send_message("chat_id_mock", message) #add chat id correctly

    def get_history(self, user_id: UUID, limit: int = 50) -> NotificationList:
        """
        Получение истории уведомлений

        Args:
            user_id: ID пользователя
            limit: Лимит уведомлений

        Returns:
            NotificationList: Список уведомлений
        """
        logs = self.repo.get_by_user(user_id=user_id, limit=limit) # add limit to the repo method
        return NotificationList(
            items=[
                NotificationLogResponse(
                    id=log.id, user_id=log.user_id, recommendation_id=log.recommendation_id,
                    channel=log.channel, trigger_type=log.trigger_type, message=log.message,
                    delivery_status=log.delivery_status, sent_at=log.sent_at,
                )
                for log in logs
            ],
            total=len(logs),
        )
