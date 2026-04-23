from __future__ import annotations

from datetime import time
from uuid import UUID
from typing import Any

from sqlalchemy.orm import Session

from app.models import UserSettings
from app.schemas.common import NotificationChannel, NotifyFrequency
from app.repositories.base_repo import BaseRepository


class UserSettingsRepository(BaseRepository[UserSettings]):
    """Repository for the one-to-one ``UserSettings`` profile."""

    model = UserSettings

    def get_by_user(self, db: Session, user_id: UUID) -> UserSettings | None:
        """Return notification/settings record for a user by primary key ``user_id``."""

        return db.get(UserSettings, user_id)

    def create_default(self, db: Session, *, user_id: UUID) -> UserSettings:
        """Create a default settings record for a newly registered user.

        The exact defaults are opinionated project defaults and can later be
        changed in one place without touching service logic.
        """

        settings = UserSettings(
            user_id=user_id,
            weekday_wake_up=time(7, 0),
            weekday_bedtime=time(23, 0),
            weekend_wake_up=time(9, 0),
            weekend_bedtime=time(0, 0),
            notify_channel=NotificationChannel.EMAIL,
            notify_window_start=time(9, 0),
            notify_window_end=time(21, 0),
            notify_frequency=NotifyFrequency.DAILY,
            reminders_enabled=True,
        )
        db.add(settings)
        db.flush()
        db.refresh(settings)
        return settings

    def update(
        self,
        db: Session,
        *,
        settings: UserSettings,
        weekday_wake_up: time | None = None,
        weekday_bedtime: time | None = None,
        weekend_wake_up: time | None = None,
        weekend_bedtime: time | None = None,
        channel: NotificationChannel | None = None,
        window_start: time | None = None,
        window_end: time | None = None,
        frequency: NotifyFrequency | None = None,
        enabled: bool | None = None,
    ) -> UserSettings:
        """Update only the provided settings fields and leave the rest unchanged."""

        update_data: dict[str, Any] = {}

        if weekday_wake_up is not None:
            update_data["weekday_wake_up"] = weekday_wake_up
        if weekday_bedtime is not None:
            update_data["weekday_bedtime"] = weekday_bedtime
        if weekend_wake_up is not None:
            update_data["weekend_wake_up"] = weekend_wake_up
        if weekend_bedtime is not None:
            update_data["weekend_bedtime"] = weekend_bedtime
        if channel is not None:
            update_data["notify_channel"] = channel
        if window_start is not None:
            update_data["notify_window_start"] = window_start
        if window_end is not None:
            update_data["notify_window_end"] = window_end
        if frequency is not None:
            update_data["notify_frequency"] = frequency
        if enabled is not None:
            update_data["reminders_enabled"] = enabled

        if update_data:
            return super().update(db, db_obj=settings, obj_in=update_data)

        return settings

    def upsert(
        self,
        db: Session,
        *,
        user_id: UUID,
        weekday_wake_up: time,
        weekday_bedtime: time,
        weekend_wake_up: time,
        weekend_bedtime: time,
        notify_channel: NotificationChannel,
        notify_window_start: time,
        notify_window_end: time,
        notify_frequency: NotifyFrequency,
        reminders_enabled: bool,
    ) -> UserSettings:
        """Create settings if they do not exist yet, otherwise fully overwrite them.

        This method is convenient for forms that always submit the entire settings
        payload at once.
        """

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
