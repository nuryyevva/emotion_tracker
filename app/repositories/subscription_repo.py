from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subscription, SubscriptionStatus
from app.repositories.base_repo import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for subscription history and current billing state."""

    model = Subscription

    def create(
        self,
        db: Session,
        *,
        user_id: UUID,
        plan: str,
        status: SubscriptionStatus = SubscriptionStatus.TRIAL,
        started_at: datetime | None = None,
        expires_at: datetime | None = None,
        provider: str | None = None,
        external_payment_id: str | None = None,
    ) -> Subscription:
        """Create a new subscription record for a user."""

        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            status=status,
            started_at=started_at,
            expires_at=expires_at,
            provider=provider,
            external_payment_id=external_payment_id,
        )
        db.add(subscription)
        db.flush()
        db.refresh(subscription)
        return subscription

    def get_by_user(self, db: Session, user_id: UUID) -> Subscription | None:
        """Return the most recent subscription of a user."""

        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.started_at.desc())
        )
        return db.scalar(stmt)

    def list_by_user(self, db: Session, user_id: UUID) -> list[Subscription]:
        """Return all subscriptions of a user from newest to oldest."""

        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.started_at.desc())
        )
        return list(db.scalars(stmt))
