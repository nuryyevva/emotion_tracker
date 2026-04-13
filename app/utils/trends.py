from typing import Any, List, Dict


def detect_consecutive_threshold(
        records: List[Dict[str, Any]],
        metric_name: str,
        threshold: int,
        consecutive_days: int
) -> bool:
    """
    Обнаруживает последовательные дни, где метрика превышает порог

    Args:
        records: Список записей с данными
        metric_name: Название метрики для проверки
        threshold: Пороговое значение
        consecutive_days: Количество последовательных дней

    Returns:
        bool: True если найдено последовательных дней больше или равно consecutive_days
    """
    if not records or len(records) < consecutive_days:
        return False

    consecutive_count = 0

    for record in records:
        metric_value = record.get(metric_name, 0)

        if metric_value >= threshold:
            consecutive_count += 1
            if consecutive_count >= consecutive_days:
                return True
        else:
            consecutive_count = 0

    return False


def calculate_metric_improvement(
        records: List[Dict[str, Any]],
        metric_name: str,
        delta: int,
        period_days: int = 14
) -> bool:
    """
    Вычисляет улучшение метрики за период

    Args:
        records: Список записей с данными
        metric_name: Название метрики
        delta: Требуемое улучшение
        period_days: Период в днях

    Returns:
        bool: True если улучшение достигнуто
    """
    if not records or len(records) < period_days:
        return False

    # Берем первую треть и последнюю треть периода
    first_third = records[:period_days // 3]
    last_third = records[-period_days // 3:]

    if not first_third or not last_third:
        return False

    first_avg = sum(r.get(metric_name, 0) for r in first_third) / len(first_third)
    last_avg = sum(r.get(metric_name, 0) for r in last_third) / len(last_third)

    improvement = last_avg - first_avg

    return improvement >= delta


def get_weekday_patterns(
        records: List[Dict[str, Any]],
        metric_name: str
) -> Dict[int, float]:
    """
    Получает паттерны по дням недели

    Args:
        records: Список записей с данными (должны содержать поле 'weekday' или 'date')
        metric_name: Название метрики

    Returns:
        Dict[int, float]: Словарь {день_недели: среднее_значение}
    """
    from collections import defaultdict
    from datetime import date

    weekday_values = defaultdict(list)

    for record in records:
        # Получаем день недели
        if 'weekday' in record:
            weekday = record['weekday']
        elif 'date' in record:
            record_date = record['date']
            if isinstance(record_date, str):
                from datetime import datetime
                record_date = datetime.fromisoformat(record_date).date()
            weekday = record_date.weekday()
        else:
            continue

        metric_value = record.get(metric_name)
        if metric_value is not None:
            weekday_values[weekday].append(metric_value)

    # Вычисляем средние
    result = {}
    for weekday, values in weekday_values.items():
        if values:
            result[weekday] = sum(values) / len(values)

    return result


def calculate_moving_average(values: List[float], window_size: int) -> List[float]:
    """
    Вычисляет скользящее среднее

    Args:
        values: Список значений
        window_size: Размер окна

    Returns:
        List[float]: Список скользящих средних
    """
    if not values or window_size <= 0:
        return []

    if window_size > len(values):
        return []

    moving_averages = []

    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        avg = sum(window) / window_size
        moving_averages.append(avg)

    return moving_averages