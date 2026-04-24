from typing import Optional
import logging
from uuid import UUID

from app.core.database import SessionLocal
from app.services.notification_service import NotificationService
from app.core.bot import TelegramBotService
from app.core.config import settings

logger = logging.getLogger(__name__)


# Имитация декоратора shared_task (без реального Celery)
def shared_task(func):
    """Декоратор для имитации Celery task"""
    func.delay = func
    return func


@shared_task
def send_daily_reminder(user_id_str: str) -> bool:
    """
    Отправляет ежедневное напоминание пользователю через NotificationService

    Args:
        user_id_str: ID пользователя в виде строки

    Returns:
        bool: True если напоминание отправлено успешно
    """
    logger.info(f"Sending daily reminder to user {user_id_str}")

    try:
        db = SessionLocal()
        try:
            notification_service = NotificationService(db)
            notification_service.send_daily_reminder(UUID(user_id_str))
            logger.info(f"Daily reminder sent successfully to user {user_id_str}")
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to send daily reminder to {user_id_str}: {e}")
        return False


@shared_task
def send_trend_alert(user_id_str: str, trigger_type: str) -> bool:
    """
    Отправляет алерт об изменении тренда через NotificationService

    Args:
        user_id_str: ID пользователя в виде строки
        trigger_type: Тип триггера (high_intensity, low_intensity, rising_intensity и т.д.)

    Returns:
        bool: True если алерт отправлен успешно
    """
    logger.info(f"Sending trend alert to user {user_id_str}, trigger: {trigger_type}")

    try:
        db = SessionLocal()
        try:
            notification_service = NotificationService(db)
            notification_service.send_trend_alert(UUID(user_id_str), trigger_type)
            logger.info(f"Trend alert sent successfully to user {user_id_str}")
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to send trend alert to {user_id_str}: {e}")
        return False


@shared_task
def send_welcome_email(user_id_str: str, email: str) -> bool:
    """
    Отправляет приветственное письмо новому пользователю

    Args:
        user_id_str: ID пользователя
        email: Email пользователя

    Returns:
        bool: True если письмо отправлено

    NOTE: Функция пока не реализована (заглушка)
    """
    # TODO: Реализовать отправку приветственного письма
    # Пока не реализовано согласно заданию
    logger.info(f"Welcome email would be sent to {email} (user: {user_id_str}) - NOT IMPLEMENTED YET")

    print(f"[WELCOME_EMAIL] NOT IMPLEMENTED: To: {email}, User: {user_id_str}")

    # Возвращаем True для имитации успешной отправки
    return True


@shared_task
def start_telegram_bot() -> bool:
    """
    Запускает Telegram бота для обработки сообщений и отправки напоминаний
    
    Returns:
        bool: True если бот запущен успешно
    """
    logger.info("Starting Telegram bot...")
    
    try:
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN not configured, skipping bot startup")
            return False
            
        db = SessionLocal()
        try:
            bot_service = TelegramBotService(
                db=db,
                bot_token=settings.TELEGRAM_BOT_TOKEN.get_secret_value(),
                web_app_url=f"{settings.FRONTEND_URL}/survey",
            )
            bot_service.start()
            logger.info("Telegram bot started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
        return False