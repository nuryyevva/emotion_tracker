from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subscription, SubscriptionStatus


class SubscriptionRepository:
    def create(
        self,
        db: Session,
        *,
        user_id: UUID,
        plan: str,
        status: SubscriptionStatus = SubscriptionStatus.TRIAL,
        started_at=None,
        expires_at=None,
        provider: str | None = None,
        external_payment_id: str | None = None,
    ) -> Subscription:
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
        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.started_at.desc())
        )
        return db.scalar(stmt)

    def list_by_user(self, db: Session, user_id: UUID) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.started_at.desc())
        )
        return list(db.scalars(stmt))
