from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import UserCopingMethod
from app.repositories.base_repo import BaseRepository


class UserCopingMethodRepository(BaseRepository[UserCopingMethod]):
    """Repository for user's coping methods / self-help techniques."""

    model = UserCopingMethod

    def add(self, db: Session, *, user_id: UUID, method: str) -> UserCopingMethod:
        """Attach a coping method to the user."""

        coping_method = UserCopingMethod(user_id=user_id, method=method)
        db.add(coping_method)
        db.flush()
        db.refresh(coping_method)
        return coping_method

    def list_by_user(self, db: Session, user_id: UUID) -> list[UserCopingMethod]:
        """Return all coping methods of the user ordered from newest to oldest."""

        stmt = (
            select(UserCopingMethod)
            .where(UserCopingMethod.user_id == user_id)
            .order_by(UserCopingMethod.created_at.desc())
        )
        return list(db.scalars(stmt))

    def get_by_user(self, db: Session, *, user_id: UUID) -> list[UserCopingMethod]:
        """Architecture-friendly alias for ``list_by_user``."""

        return self.list_by_user(db, user_id)

    def get_by_user_and_name(self, db: Session, *, user_id: UUID, method: str) -> UserCopingMethod | None:
        """Return one coping method by user and method name."""

        stmt = select(UserCopingMethod).where(
            UserCopingMethod.user_id == user_id,
            UserCopingMethod.method == method,
        )
        return db.scalar(stmt)

    def remove(self, db: Session, *, user_id: UUID, method: str) -> bool:
        """Delete a coping method entry and return whether anything was deleted."""

        stmt = delete(UserCopingMethod).where(
            UserCopingMethod.user_id == user_id,
            UserCopingMethod.method == method,
        )
        result = db.execute(stmt)
        return result.rowcount > 0

    def delete_by_user_and_name(self, db: Session, *, user_id: UUID, method: str) -> bool:
        """Architecture-friendly alias for deleting by method name."""

        return self.remove(db, user_id=user_id, method=method)
