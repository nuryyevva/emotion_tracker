from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import UserCopingMethod
from app.repositories.base_repo import BaseRepository


class UserCopingMethodRepository(BaseRepository[UserCopingMethod]):
    """Repository for user's coping methods / self-help techniques."""

    def __init__(self, db: Session):
        super().__init__(db)

    model = UserCopingMethod

    def list_by_user(self, user_id: UUID) -> list[UserCopingMethod]:
        """Return all coping methods of the user ordered from newest to oldest."""

        stmt = (
            select(UserCopingMethod)
            .where(UserCopingMethod.user_id == user_id)
            .order_by(UserCopingMethod.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_by_user(self, *, user_id: UUID) -> list[UserCopingMethod]:
        """Architecture-friendly alias for ``list_by_user``."""

        return self.list_by_user(user_id)

    def get_by_user_and_name(self, *, user_id: UUID, method: str) -> UserCopingMethod | None:
        """Return one coping method by user and method name."""

        stmt = select(UserCopingMethod).where(
            UserCopingMethod.user_id == user_id,
            UserCopingMethod.method == method,
        )
        return self.db.scalar(stmt)

    def delete_by_user_and_name(self, *, user_id: UUID, method: str) -> bool:
        """Architecture-friendly alias for deleting by method name."""

        obj = self.get_by_user_and_name(user_id=user_id, method=method)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
