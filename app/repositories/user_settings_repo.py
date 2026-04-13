from __future__ import annotations

from datetime import time
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import NotifyChannel, NotifyFrequency, UserSettings


class UserSettingsRepository:
    def get_by_user(self, db: Session, user_id: UUID) -> UserSettings | None:
        return db.get(UserSettings, user_id)

    def upsert(
        self,
        db: Session,
        *,
        user_id: UUID,
        weekday_wake_up: time,
        weekday_bedtime: time,
        weekend_wake_up: time,
        weekend_bedtime: time,
        notify_channel: NotifyChannel,
        notify_window_start: time,
        notify_window_end: time,
        notify_frequency: NotifyFrequency,
        reminders_enabled: bool,
    ) -> UserSettings:
        settings = db.get(UserSettings, user_id)
        if settings is None:
            settings = UserSettings(
                user_id=user_id,
                weekday_wake_up=weekday_wake_up,
                weekday_bedtime=weekday_bedtime,
                weekend_wake_up=weekend_wake_up,
                weekend_bedtime=weekend_bedtime,
                notify_channel=notify_channel,
                notify_window_start=notify_window_start,
                notify_window_end=notify_window_end,
                notify_frequency=notify_frequency,
                reminders_enabled=reminders_enabled,
            )
            db.add(settings)
        else:
            settings.weekday_wake_up = weekday_wake_up
            settings.weekday_bedtime = weekday_bedtime
            settings.weekend_wake_up = weekend_wake_up
            settings.weekend_bedtime = weekend_bedtime
            settings.notify_channel = notify_channel
            settings.notify_window_start = notify_window_start
            settings.notify_window_end = notify_window_end
            settings.notify_frequency = notify_frequency
            settings.reminders_enabled = reminders_enabled

        db.flush()
        db.refresh(settings)
        return settings
