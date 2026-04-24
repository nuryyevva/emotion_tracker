from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subscription
from app.repositories.base_repo import BaseRepository
from app.schemas.common import SubscriptionStatus

class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for subscription history and current billing state."""

    def __init__(self, db: Session):
        super().__init__(db)

    model = Subscription

    def get_by_user(self, user_id: UUID) -> Subscription | None:
        """Return the most recent subscription of a user."""

        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.started_at.desc())
        )
        return self.db.scalar(stmt)

    def list_by_user(self, user_id: UUID) -> list[Subscription]:
        """Return all subscriptions of a user from newest to oldest."""

        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.started_at.desc())
        )
        return list(self.db.scalars(stmt))
