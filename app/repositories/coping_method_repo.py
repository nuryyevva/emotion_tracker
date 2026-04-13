from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import UserCopingMethod


class UserCopingMethodRepository:
    def add(self, db: Session, *, user_id: UUID, method: str) -> UserCopingMethod:
        coping_method = UserCopingMethod(user_id=user_id, method=method)
        db.add(coping_method)
        db.flush()
        db.refresh(coping_method)
        return coping_method

    def list_by_user(self, db: Session, user_id: UUID) -> list[UserCopingMethod]:
        stmt = (
            select(UserCopingMethod)
            .where(UserCopingMethod.user_id == user_id)
            .order_by(UserCopingMethod.created_at.desc())
        )
        return list(db.scalars(stmt))

    def remove(self, db: Session, *, user_id: UUID, method: str) -> bool:
        stmt = delete(UserCopingMethod).where(
            UserCopingMethod.user_id == user_id,
            UserCopingMethod.method == method,
        )
        result = db.execute(stmt)
        return result.rowcount > 0
