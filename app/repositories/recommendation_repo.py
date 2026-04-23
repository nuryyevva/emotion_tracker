from __future__ import annotations

import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Recommendation
from app.repositories.base_repo import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    """Repository for recommendation templates shown to users."""

    def __init__(self, db: Session):
        super().__init__(db)

    model = Recommendation

    def get_by_trigger_type(
        self,
        *,
        trigger_type: str,
        is_active: bool = True,
    ) -> list[Recommendation]:
        """Return active recommendations suitable for a specific trigger."""

        stmt = (
            select(Recommendation)
            .where(
                Recommendation.trigger_type == trigger_type,
                Recommendation.is_active == is_active,
            )
            .order_by(Recommendation.priority.desc(), Recommendation.id.asc())
        )
        return list(self.db.scalars(stmt))

    def get_random_active(
        self,
        *,
        trigger_type: str,
        exclude_ids: list[UUID] | None = None,
    ) -> Recommendation | None:
        """Return one random active recommendation, optionally excluding recent IDs."""

        recommendations = self.get_by_trigger_type(trigger_type=trigger_type, is_active=True)
        if exclude_ids:
            recommendations = [recommendation for recommendation in recommendations if recommendation.id not in exclude_ids]
        return random.choice(recommendations) if recommendations else None

    def get_by_category(
        self,
        *,
        category: str,
        is_active: bool = True,
    ) -> list[Recommendation]:
        """Return recommendations filtered by semantic category."""

        stmt = (
            select(Recommendation)
            .where(
                Recommendation.category == category,
                Recommendation.is_active == is_active,
            )
            .order_by(Recommendation.priority.desc(), Recommendation.id.asc())
        )
        return list(self.db.scalars(stmt))
