from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

# Константа для ротации напоминаний
REMINDER_ROTATION_DAYS = 7


def select_recommendation(
        candidates: List[Dict[str, Any]],
        recent_ids: List[UUID],
        context: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Выбирает подходящую рекомендацию из кандидатов

    Args:
        candidates: Список кандидатов на рекомендацию
        recent_ids: Список ID недавно показанных рекомендаций
        context: Контекст для выбора (время, эмоции и т.д.)

    Returns:
        Optional[Dict[str, Any]]: Выбранная рекомендация или None
    """
    if not candidates:
        return None

    # Фильтруем недавно показанные
    filtered = [c for c in candidates if c.get('id') not in recent_ids]

    if not filtered:
        return None

    # Если есть контекст, фильтруем по контексту
    if context:
        emotion_type = context.get('emotion_type')
        if emotion_type:
            emotion_matched = [
                c for c in filtered
                if c.get('target_emotion') == emotion_type
            ]
            if emotion_matched:
                filtered = emotion_matched

    # Сортируем по приоритету
    filtered.sort(key=lambda x: x.get('priority', 0), reverse=True)

    return filtered[0] if filtered else None


def check_rotation_rule(
        last_shown_date: Optional[datetime],
        min_days_interval: int = REMINDER_ROTATION_DAYS,
        now: Optional[datetime] = None
) -> bool:
    """
    Проверяет правило ротации рекомендаций

    Args:
        last_shown_date: Дата последнего показа
        min_days_interval: Минимальный интервал в днях
        now: Текущая дата

    Returns:
        bool: True если можно показать новую рекомендацию
    """
    if last_shown_date is None:
        return True

    if now is None:
        now = datetime.utcnow()

    days_since_last = (now - last_shown_date).days

    return days_since_last >= min_days_interval


def contextualize_message(
        message: str,
        hour: int,
        user_name: Optional[str] = None
) -> str:
    """
    Адаптирует сообщение под контекст

    Args:
        message: Исходное сообщение
        hour: Текущий час (0-23)
        user_name: Имя пользователя

    Returns:
        str: Адаптированное сообщение
    """
    contextualized = message

    # Добавляем имя пользователя
    if user_name:
        contextualized = contextualized.replace("{name}", user_name)

    # Время суток
    if 5 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 17:
        greeting = "Добрый день"
    elif 17 <= hour < 22:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    contextualized = contextualized.replace("{greeting}", greeting)

    return contextualized


def categorize_trigger(
        metric: str,
        value: int,
        trend: Optional[str] = None
) -> Optional[str]:
    """
    Категоризирует триггер на основе метрики и значения

    Args:
        metric: Название метрики (intensity, sleep_hours, activity)
        value: Значение метрики
        trend: Тренд (increasing, decreasing, stable)

    Returns:
        Optional[str]: Категория триггера или None
    """
    if metric == "intensity":
        if value >= 8:
            return "high_intensity"
        elif value <= 3:
            return "low_intensity"
        elif trend == "increasing":
            return "rising_intensity"
        elif trend == "decreasing":
            return "falling_intensity"

    elif metric == "sleep_hours":
        if value < 6:
            return "sleep_deprivation"
        elif value > 9:
            return "excess_sleep"

    elif metric == "activity":
        if value < 30:
            return "low_activity"
        elif value > 120:
            return "high_activity"

    return None