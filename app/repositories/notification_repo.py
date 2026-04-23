from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import NotificationLog
from app.repositories.base_repo import BaseRepository
from app.schemas.common import DeliveryStatus


class NotificationRepository(BaseRepository[NotificationLog]):
    """Repository for notification delivery history."""

    def __init__(self, db: Session):
        super().__init__(db)

    model = NotificationLog

    def create_log(
        self,
        *,
        user_id: UUID,
        recommendation_id: UUID | None,
        channel: str,
        trigger_type: str,
        message: str,
    ) -> NotificationLog:
        """Create a notification log entry before or during delivery."""

        return self.create(
            obj_in={
                "user_id": user_id,
                "recommendation_id": recommendation_id,
                "channel": channel,
                "trigger_type": trigger_type,
                "message": message,
            },
        )

    def mark_as_sent(self, *, notification: NotificationLog) -> NotificationLog:
        """Mark an existing notification as successfully delivered."""

        return self.update(
            db_obj=notification,
            obj_in={"delivery_status": DeliveryStatus.SENT},
        )

    def mark_as_failed(self, *, notification: NotificationLog) -> NotificationLog:
        """Mark an existing notification as failed."""

        return self.update(
            db_obj=notification,
            obj_in={"delivery_status": DeliveryStatus.FAILED},
        )

    def get_by_user(self, *, user_id: UUID) -> list[NotificationLog]:
        """Return notification history for a user ordered from newest to oldest."""

        stmt = (
            select(NotificationLog)
            .where(NotificationLog.user_id == user_id)
            .order_by(NotificationLog.sent_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_recent_by_trigger(
        self,
        *,
        user_id: UUID,
        trigger_type: str,
        days: int = 7,
    ) -> list[NotificationLog]:
        """Return the most recent notifications with the given trigger type.

        Note:
            The ``days`` parameter currently limits how many latest matching
            notifications are returned. It does not yet filter by ``sent_at``
            inside an actual rolling N-day time window.
        """

        notifications = self.get_by_user(user_id=user_id)
        return [notification for notification in notifications if notification.trigger_type == trigger_type][:days]
