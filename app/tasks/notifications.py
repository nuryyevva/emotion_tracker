from typing import Optional
import logging

logger = logging.getLogger(__name__)


# Имитация декоратора shared_task (без реального Celery)
def shared_task(func):
    """Декоратор для имитации Celery task"""
    func.delay = func
    return func


@shared_task
def send_daily_reminder(user_id_str: str) -> bool:
    """
    Отправляет ежедневное напоминание пользователю

    Args:
        user_id_str: ID пользователя в виде строки

    Returns:
        bool: True если напоминание отправлено успешно
    """
    logger.info(f"Sending daily reminder to user {user_id_str}")

    try:
        print(f"[DAILY_REMINDER] Sent to user: {user_id_str}")

        return True
    except Exception as e:
        logger.error(f"Failed to send daily reminder to {user_id_str}: {e}")
        return False


@shared_task
def send_trend_alert(user_id_str: str, trigger_type: str) -> bool:
    """
    Отправляет алерт об изменении тренда

    Args:
        user_id_str: ID пользователя в виде строки
        trigger_type: Тип триггера (high_intensity, low_intensity, rising_intensity и т.д.)

    Returns:
        bool: True если алерт отправлен успешно
    """
    logger.info(f"Sending trend alert to user {user_id_str}, trigger: {trigger_type}")

    alert_messages = {
        "high_intensity": "Заметили, что интенсивность эмоций высокая. Хотите поговорить?",
        "low_intensity": "Последнее время эмоции приглушены. Как вы себя чувствуете?",
        "rising_intensity": "Интенсивность эмоций растет. Давайте разберемся, что происходит.",
        "falling_intensity": "Интенсивность эмоций снижается. Что изменилось в последнее время?",
        "sleep_deprivation": "Недостаток сна может влиять на настроение. Отдохните.",
        "low_activity": "Мало активности? Попробуйте небольшую прогулку."
    }

    try:
        message = alert_messages.get(trigger_type, "Замечены изменения в ваших эмоциональных паттернах.")

        print(f"[TREND_ALERT] User: {user_id_str}, Trigger: {trigger_type}")
        print(f"[TREND_ALERT] Message: {message}")

        return True
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