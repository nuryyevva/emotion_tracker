from typing import Any, Dict
import re


def validate_timezone(timezone: str) -> bool:
    """
    Проверяет корректность временной зоны

    Args:
        timezone: Название временной зоны

    Returns:
        bool: True если временная зона существует
    """
    import pytz

    try:
        pytz.timezone(timezone)
        return True
    except:
        return False


def validate_sleep_time(time_str: str) -> bool:
    """
    Проверяет корректность времени сна

    Args:
        time_str: Строка времени (формат "HH:MM")

    Returns:
        bool: True если формат корректный
    """
    if not time_str:
        return False

    pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'

    if not re.match(pattern, time_str):
        return False

    return True


def validate_note_content(note: str) -> Dict[str, Any]:
    """
    Проверяет содержимое заметки

    Args:
        note: Текст заметки

    Returns:
        Dict[str, Any]: Результат валидации с полями is_valid, error, sanitized
    """
    if not note:
        return {
            "is_valid": True,
            "error": None,
            "sanitized": ""
        }

    # Максимальная длина
    MAX_LENGTH = 1000
    if len(note) > MAX_LENGTH:
        return {
            "is_valid": False,
            "error": f"Note is too long. Maximum {MAX_LENGTH} characters",
            "sanitized": note[:MAX_LENGTH]
        }

    # Проверка на опасные символы
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'onclick=',
        r'<iframe'
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, note, re.IGNORECASE):
            return {
                "is_valid": False,
                "error": "Note contains forbidden content",
                "sanitized": re.sub(pattern, '[removed]', note, flags=re.IGNORECASE)
            }

    # Очистка текста
    sanitized = re.sub(r'[<>{}]', '', note)
    sanitized = sanitized.strip()

    return {
        "is_valid": True,
        "error": None,
        "sanitized": sanitized
    }


def validate_password_strength(password: str) -> bool:
    """
    Проверяет сложность пароля

    Args:
        password: Пароль для проверки

    Returns:
        bool: True если пароль достаточно сложный
    """
    if not password:
        return False

    # Минимальная длина
    if len(password) < 8:
        return False

    # Заглавная буква
    if not re.search(r'[A-Z]', password):
        return False

    # Строчная буква
    if not re.search(r'[a-z]', password):
        return False

    # Цифра
    if not re.search(r'\d', password):
        return False

    # Специальный символ (опционально, но рекомендовано)
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     return False

    return True