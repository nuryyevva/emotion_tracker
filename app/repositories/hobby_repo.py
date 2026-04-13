from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import UserHobby


class UserHobbyRepository:
    def add(self, db: Session, *, user_id: UUID, hobby: str) -> UserHobby:
        user_hobby = UserHobby(user_id=user_id, hobby=hobby)
        db.add(user_hobby)
        db.flush()
        db.refresh(user_hobby)
        return user_hobby

    def list_by_user(self, db: Session, user_id: UUID) -> list[UserHobby]:
        stmt = select(UserHobby).where(UserHobby.user_id == user_id).order_by(UserHobby.created_at.desc())
        return list(db.scalars(stmt))

    def remove(self, db: Session, *, user_id: UUID, hobby: str) -> bool:
        stmt = delete(UserHobby).where(UserHobby.user_id == user_id, UserHobby.hobby == hobby)
        result = db.execute(stmt)
        return result.rowcount > 0
