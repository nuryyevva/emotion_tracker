from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user, CurrentUserContext
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationPreferencesUpdate,
    NotificationLogResponse,
    NotificationList,
    NotificationTestResponse,
)
from app.schemas.common import NotificationChannel

router = APIRouter(prefix="/notifications")


@router.put("/preferences", response_model=dict)
async def put_notifications_preferences(
    request: NotificationPreferencesUpdate,
    user: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user notification preferences."""
    service = NotificationService(db)
    updated_settings = service.update_preferences(
        user_id=user.user_id,
        channel=request.channel,
        window_start=request.window_start,
        window_end=request.window_end,
        frequency=request.frequency,
        reminders_enabled=request.reminders_enabled,
        trend_alerts_enabled=request.trend_alerts_enabled,
        positive_feedback_enabled=request.positive_feedback_enabled,
    )
    return {
        "channel": updated_settings.notify_channel.value if hasattr(updated_settings.notify_channel, 'value') else str(updated_settings.notify_channel),
        "window_start": updated_settings.notify_window_start.strftime("%H:%M"),
        "window_end": updated_settings.notify_window_end.strftime("%H:%M"),
        "frequency": updated_settings.notify_frequency.value if hasattr(updated_settings.notify_frequency, 'value') else str(updated_settings.notify_frequency),
        "reminders_enabled": updated_settings.reminders_enabled,
        "updated_at": updated_settings.updated_at,
    }


@router.get("", response_model=NotificationList)
async def get_notifications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    unread_only: bool = False,
    user: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's notification history."""
    service = NotificationService(db)
    return service.get_history(user_id=user.user_id, limit=limit)


@router.post("/test", response_model=NotificationTestResponse)
async def post_notifications_test(
    user: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a test notification to the user."""
    service = NotificationService(db)
    channel = service.send_test_notification(user_id=user.user_id)
    return NotificationTestResponse(
        message="Test notification sent successfully",
        channel=channel,
        sent_at=datetime.now(),
    )