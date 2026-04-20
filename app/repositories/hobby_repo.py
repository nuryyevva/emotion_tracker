from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import UserHobby
from app.repositories.base_repo import BaseRepository


class UserHobbyRepository(BaseRepository[UserHobby]):
    """Repository for user's hobby list."""

    model = UserHobby

    def add(self, db: Session, *, user_id: UUID, hobby: str) -> UserHobby:
        """Attach a new hobby string to the user."""

        user_hobby = UserHobby(user_id=user_id, hobby=hobby)
        db.add(user_hobby)
        db.flush()
        db.refresh(user_hobby)
        return user_hobby

    def list_by_user(self, db: Session, user_id: UUID) -> list[UserHobby]:
        """Return all hobbies of the user ordered from newest to oldest."""

        stmt = select(UserHobby).where(UserHobby.user_id == user_id).order_by(UserHobby.created_at.desc())
        return list(db.scalars(stmt))

    def get_by_user(self, db: Session, *, user_id: UUID) -> list[UserHobby]:
        """Architecture-friendly alias for ``list_by_user``."""

        return self.list_by_user(db, user_id)

    def get_by_user_and_name(self, db: Session, *, user_id: UUID, hobby: str) -> UserHobby | None:
        """Return a specific hobby entry by user and hobby name."""

        stmt = select(UserHobby).where(UserHobby.user_id == user_id, UserHobby.hobby == hobby)
        return db.scalar(stmt)

    def remove(self, db: Session, *, user_id: UUID, hobby: str) -> bool:
        """Delete a hobby entry and return ``True`` if a row was removed."""

        stmt = delete(UserHobby).where(UserHobby.user_id == user_id, UserHobby.hobby == hobby)
        result = db.execute(stmt)
        return result.rowcount > 0

    def delete_by_user_and_name(self, db: Session, *, user_id: UUID, hobby: str) -> bool:
        """Architecture-friendly alias for deleting a hobby by its name."""

        return self.remove(db, user_id=user_id, hobby=hobby)
