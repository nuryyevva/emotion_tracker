from datetime import datetime, time, timedelta
from typing import Any, List, Dict, Optional
import pytz


def convert_to_timezone(dt_utc: datetime, timezone_str: str) -> datetime:
    """
    Конвертирует UTC время в указанную временную зону

    Args:
        dt_utc: UTC datetime
        timezone_str: Название временной зоны (например, 'Europe/Moscow')

    Returns:
        datetime: Время в указанной временной зоне
    """
    try:
        tz = pytz.timezone(timezone_str)
        if dt_utc.tzinfo is None:
            dt_utc = pytz.UTC.localize(dt_utc)
        return dt_utc.astimezone(tz)
    except:
        return dt_utc


def get_user_day_start(
        timezone_str: str,
        now_utc: Optional[datetime] = None
) -> datetime:
    if now_utc is None:
        now_utc = datetime.utcnow()

    user_time = convert_to_timezone(now_utc, timezone_str)
    user_day_start = user_time.replace(hour=0, minute=0, second=0, microsecond=0)

    return user_day_start.astimezone(pytz.UTC).replace(tzinfo=None)


def is_within_notification_window(
        start_time: str,
        end_time: str,
        timezone_str: str,
        now_utc: Optional[datetime] = None
) -> bool:
    """
    Проверяет, находится ли текущее время в окне уведомлений

    Args:
        start_time: Время начала (формат "HH:MM")
        end_time: Время окончания (формат "HH:MM")
        timezone_str: Временная зона пользователя
        now_utc: Текущее UTC время

    Returns:
        bool: True если текущее время в окне уведомлений
    """
    if now_utc is None:
        now_utc = datetime.utcnow()

    user_time = convert_to_timezone(now_utc, timezone_str)
    current = user_time.time()

    start_hour, start_min = map(int, start_time.split(':'))
    end_hour, end_min = map(int, end_time.split(':'))

    start = time(start_hour, start_min)
    end = time(end_hour, end_min)

    if start <= end:
        return start <= current <= end
    else:
        # Окно переходит через полночь
        return current >= start or current <= end


def calculate_streak(records: List[Dict[str, Any]]) -> int:
    """
    Вычисляет текущую серию (streak) последовательных дней

    Args:
        records: Список записей с полем 'date'

    Returns:
        int: Длина текущей серии
    """
    if not records:
        return 0

    from datetime import date, timedelta

    dates = []
    for record in records:
        record_date = record.get('date')
        if record_date:
            if isinstance(record_date, str):
                from datetime import datetime
                record_date = datetime.fromisoformat(record_date).date()
            dates.append(record_date)

    if not dates:
        return 0

    unique_dates = sorted(set(dates), reverse=True)

    streak = 0
    expected_date = date.today()

    for d in unique_dates:
        if d == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break

    return streak