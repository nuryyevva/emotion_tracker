"""
Business Constants

Hardcoded business rules from System Analysis Document.
Centralized for easy adjustment and consistency.
"""

# =============================================================================
# FREEMIUM LIMITS (From System Analysis)
# =============================================================================

FREE_ANALYTICS_DAYS: int = 90
"""Free users can view analytics for up to 90 days (3 months)"""

PRO_ANALYTICS_DAYS: int = 365
"""Pro users can view analytics for up to 365 days (1 year)"""

MAX_EXPORT_DAYS: int = 365
"""Maximum period for data export"""

MIN_CORRELATION_DAYS: int = 14
"""Minimum days required for statistical correlation analysis"""

# =============================================================================
# NOTIFICATION TRIGGERS (From System Analysis - Банк рекомендаций)
# =============================================================================

FATIGUE_THRESHOLD: int = 8
"""Fatigue level considered 'high' (1-10 scale)"""

FATIGUE_CONSECUTIVE_DAYS: int = 3
"""Consecutive days of high fatigue to trigger notification"""

ANXIETY_THRESHOLD: int = 7
"""Anxiety level considered 'high' (1-10 scale)"""

ANXIETY_CONSECUTIVE_DAYS: int = 5
"""Consecutive days of high anxiety to trigger notification"""

MOOD_IMPROVEMENT_DELTA: int = 3
"""Mood points increase to trigger positive feedback"""

SLEEP_DEVIATION_HOURS: int = 2
"""Hours deviation from sleep schedule to trigger reminder"""

# =============================================================================
# VALIDATION LIMITS
# =============================================================================

MAX_NOTE_LENGTH: int = 500
"""Maximum characters for emotion note (from System Analysis)"""

PASSWORD_MIN_LENGTH: int = 8
"""Minimum password length"""

MAX_HOBBY_LENGTH: int = 50
"""Maximum characters for hobby name"""

MAX_COPING_METHOD_LENGTH: int = 100
"""Maximum characters for coping method"""

MAX_COMMENT_LENGTH: int = 1000
"""Maximum characters for Pro comment"""

# =============================================================================
# NOTIFICATION RULES
# =============================================================================

REMINDER_ROTATION_DAYS: int = 7
"""Do not show same recommendation twice within this period"""

DEFAULT_NOTIFY_WINDOW_START: str = "08:00"
"""Default notification window start"""

DEFAULT_NOTIFY_WINDOW_END: str = "22:00"
"""Default notification window end"""

# =============================================================================
# TONE OF VOICE (From System Analysis)
# =============================================================================

AUTONOMY_SUPPORTIVE_PREFIX: str = "Возможно, стоит..."
"""Prefix for autonomy-supportive suggestions"""

DIRECTIVE_PREFIX_AVOID: str = "Вам нужно..."
"""Prefix to avoid (too directive)"""

SUPPORTIVE_MESSAGES = {
    "fatigue_high": "Заметил, что усталость растёт. Возможно, стоит добавить перерыв?",
    "anxiety_high": "Тревожность держится высоко. Хотите попробовать дыхательное упражнение?",
    "mood_improvement": "Здорово! Настроение улучшилось. Что помогло?",
}
"""Pre-defined supportive messages for common triggers"""

# =============================================================================
# SUBSCRIPTION
# =============================================================================

PRO_FEATURES = {
    "llm_insights",
    "export_csv",
    "export_pdf",
    "comments",
    "correlations",
    "deep_analytics",
    "unlimited_history",
}
"""Set of features requiring Pro subscription"""
