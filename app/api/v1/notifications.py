from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

router = APIRouter(prefix="/notifications")


@router.put("/notifications/preferences", response_model=NotificationPreferencesResponse)
async def put_notifications_preferences(request: PreferencesUpdateRequest):
    return NotificationPreferencesResponse(
        email_enabled=request.email_enabled if request.email_enabled is not None else True,
        telegram_enabled=request.telegram_enabled if request.telegram_enabled is not None else False,
        daily_summary=request.daily_summary if request.daily_summary is not None else True,
        weekly_report=request.weekly_report if request.weekly_report is not None else True,
        reminder_time=request.reminder_time or "20:00",
        updated_at=datetime.now()
    )


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    unread_only: bool = False
):
    return [
        NotificationResponse(
            id=str(uuid4()),
            title="Daily Reminder",
            message="Don't forget to log your emotion today!",
            type="reminder",
            is_read=False,
            created_at=datetime.now(),
            data={"action": "log_emotion"}
        )
    ]


@router.post("/notifications/test")
async def post_notifications_test():
    return {"message": "Test notification sent successfully"}