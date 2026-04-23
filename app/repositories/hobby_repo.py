from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import UserHobby
from app.repositories.base_repo import BaseRepository


class UserHobbyRepository(BaseRepository[UserHobby]):
    """Repository for user's hobby list."""

    def __init__(self, db: Session):
        super().__init__(db)

    model = UserHobby

    def list_by_user(self, user_id: UUID) -> list[UserHobby]:
        """Return all hobbies of the user ordered from newest to oldest."""

        stmt = select(UserHobby).where(UserHobby.user_id == user_id).order_by(UserHobby.created_at.desc())
        return list(self.db.scalars(stmt))

    def get_by_user(self, *, user_id: UUID) -> list[UserHobby]:
        """Architecture-friendly alias for ``list_by_user``."""

        return self.list_by_user(user_id)

    def get_by_user_and_name(self, *, user_id: UUID, hobby: str) -> UserHobby | None:
        """Return a specific hobby entry by user and hobby name."""

        stmt = select(UserHobby).where(UserHobby.user_id == user_id, UserHobby.hobby == hobby)
        return self.db.scalar(stmt)

    def delete_by_user_and_name(self, *, user_id: UUID, hobby: str) -> bool:
        """Architecture-friendly alias for deleting a hobby by its name."""

        obj = self.get_by_user_and_name(user_id=user_id, hobby=hobby)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
