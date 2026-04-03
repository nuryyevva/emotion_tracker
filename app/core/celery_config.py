"""
Celery Configuration

Background task processor for notifications, exports, and analytics.
Based on System Analysis: Habit formation requires timely notifications.
"""

from celery import Celery
from app.core.config import settings


# =============================================================================
# CELERY APP
# =============================================================================


celery_app = Celery(
    "emotion_tracker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.notifications",
        "app.tasks.analytics",
        "app.tasks.exports",
        "app.tasks.maintenance",
    ],
)


# =============================================================================
# CONFIGURATION
# =============================================================================


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,  # Fair task distribution
    task_routes={
        "app.tasks.notifications.*": {"queue": "notifications"},
        "app.tasks.exports.*": {"queue": "exports"},
        "app.tasks.analytics.*": {"queue": "analytics"},
        "app.tasks.maintenance.*": {"queue": "maintenance"},
    },
)


# =============================================================================
# SCHEDULED TASKS (Celery Beat)
# =============================================================================


celery_app.conf.beat_schedule = {
    "expire-subscriptions-every-hour": {
        "task": "app.tasks.maintenance.expire_subscriptions",
        "schedule": 3600.0,  # Every hour
    },
    "cleanup-old-notifications-weekly": {
        "task": "app.tasks.maintenance.cleanup_old_notifications",
        "schedule": 604800.0,  # Every week (Sunday)
    },
    "cleanup-temp-files-daily": {
        "task": "app.tasks.maintenance.cleanup_temp_files",
        "schedule": 86400.0,  # Every day
    },
    "recalculate-user-trends-daily": {
        "task": "app.tasks.analytics.recalculate_user_trends",
        "schedule": 86400.0,  # Every day at 00:00 UTC
    },
}


# =============================================================================
# INITIALIZATION
# =============================================================================


def init_celery() -> Celery:
    """
    Initialize Celery app.
    Called from app/main.py during startup.
    """
    return celery_app
