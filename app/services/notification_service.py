"""
Сервис уведомлений
"""
from uuid import UUID
from datetime import time
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.notification_repo import NotificationRepository
from app.repositories.user_settings_repo import UserSettingsRepository
from app.services.recommendation_service import RecommendationService
from app.services.user_service import UserService
from app.schemas.notification import NotificationLogResponse, NotificationList
from app.schemas.common import NotificationChannel
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
        self.settings_repo = UserSettingsRepository(db)
        self.rec_service = RecommendationService(db)
        self.user_service = UserService(db)
        self.telegram_client = TelegramProvider()

    def update_preferences(
        self,
        user_id: UUID,
        channel: Optional[NotificationChannel] = None,
        window_start: Optional[str] = None,
        window_end: Optional[str] = None,
        frequency: Optional[str] = None,
        reminders_enabled: Optional[bool] = None,
        trend_alerts_enabled: Optional[bool] = None,
        positive_feedback_enabled: Optional[bool] = None,
    ):
        """
        Обновление настроек уведомлений пользователя

        Args:
            user_id: ID пользователя
            channel: Канал уведомлений
            window_start: Время начала окна уведомлений (формат "HH:MM")
            window_end: Время окончания окна уведомлений (формат "HH:MM")
            frequency: Частота уведомлений
            reminders_enabled: Включены ли напоминания
            trend_alerts_enabled: Включены ли алерты о трендах
            positive_feedback_enabled: Включена ли положительная обратная связь

        Returns:
            Updated UserSettings object
        """
        settings = self.settings_repo.get_by_user(user_id)
        if not settings:
            settings = self.settings_repo.create_default(user_id=user_id)

        # Parse time strings if provided
        start_time = None
        end_time = None
        if window_start:
            hour, minute = map(int, window_start.split(':'))
            start_time = time(hour, minute)
        if window_end:
            hour, minute = map(int, window_end.split(':'))
            end_time = time(hour, minute)

        # Map frequency string to enum if needed
        from app.schemas.common import NotifyFrequency
        freq_enum = None
        if frequency:
            try:
                freq_enum = NotifyFrequency(frequency.lower())
            except ValueError:
                pass

        self.settings_repo.update(
            settings=settings,
            channel=channel,
            window_start=start_time,
            window_end=end_time,
            frequency=freq_enum,
            enabled=reminders_enabled,
        )

        return settings

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
        settings = self.settings_repo.get_by_user(user_id)
        if not settings:
            settings = self.settings_repo.create_default(user_id=user_id)

        # Get user for timezone and chat_id
        user = self.user_service.user_repo.get_by_id(user_id)
        if not user:
            return

        # Determine channel
        channel = settings.notify_channel

        # Send via preferred channel
        success = False
        chat_id = user.telegram_chat_id if hasattr(user, 'telegram_chat_id') else None
        
        if channel in [NotificationChannel.TELEGRAM, NotificationChannel.BOTH] and chat_id:
            success = self.telegram_client.send_trend_notification(chat_id, trigger_type, rec["message"])
        # Email sending would be implemented here if EMAIL channel is selected

        # Log
        log = self.repo.create_log(
            user_id=user_id,
            recommendation_id=rec.get("id") if isinstance(rec, dict) else None,
            channel=channel.value if hasattr(channel, 'value') else str(channel),
            trigger_type=trigger_type,
            message=rec["message"] if isinstance(rec, dict) else str(rec),
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
        settings = self.settings_repo.get_by_user(user_id)
        if not settings:
            settings = self.settings_repo.create_default(user_id=user_id)

        if not settings.reminders_enabled:
            return

        # Check window
        if not is_within_notification_window(
                settings.notify_window_start.strftime("%H:%M"),
                settings.notify_window_end.strftime("%H:%M"),
                self.user_service.user_repo.get_by_id(user_id).timezone if self.user_service.user_repo.get_by_id(user_id) else "UTC",
        ):
            return

        message = "Хотите отметить, как прошёл день? Это займёт 30 секунд."

        # Get user for chat_id
        user = self.user_service.user_repo.get_by_id(user_id)
        if not user:
            return

        channel = settings.notify_channel
        chat_id = user.telegram_chat_id if hasattr(user, 'telegram_chat_id') else None

        # Send via preferred channel
        if channel in [NotificationChannel.TELEGRAM, NotificationChannel.BOTH] and chat_id:
            self.telegram_client.send_message(chat_id, message)
        # Email sending would be implemented here if EMAIL channel is selected

    def get_history(self, user_id: UUID, limit: int = 50) -> NotificationList:
        """
        Получение истории уведомлений

        Args:
            user_id: ID пользователя
            limit: Лимит уведомлений

        Returns:
            NotificationList: Список уведомлений
        """
        logs = self.repo.get_by_user(user_id=user_id, limit=limit)
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

    def send_test_notification(self, user_id: UUID) -> NotificationChannel:
        """
        Отправка тестового уведомления

        Args:
            user_id: ID пользователя

        Returns:
            NotificationChannel: Канал, через который было отправлено уведомление
        """
        settings = self.settings_repo.get_by_user(user_id)
        if not settings:
            settings = self.settings_repo.create_default(user_id=user_id)

        user = self.user_service.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        channel = settings.notify_channel
        chat_id = user.telegram_chat_id if hasattr(user, 'telegram_chat_id') else None
        message = "🔔 Это тестовое уведомление от Emotion Tracker"

        success = False
        if channel in [NotificationChannel.TELEGRAM, NotificationChannel.BOTH] and chat_id:
            success = self.telegram_client.send_message(chat_id, message)
        # Email sending would be implemented here if EMAIL channel is selected

        # Log the test notification
        log = self.repo.create_log(
            user_id=user_id,
            recommendation_id=None,
            channel=channel.value if hasattr(channel, 'value') else str(channel),
            trigger_type="test",
            message=message,
        )
        if success:
            self.repo.mark_as_sent(notification=log)
        else:
            self.repo.mark_as_failed(notification=log)

        return channel
