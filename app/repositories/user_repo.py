from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserStatus


class UserRepository:
    def create(
        self,
        db: Session,
        *,
        email: str,
        password_hash: str,
        timezone: str,
        status: UserStatus = UserStatus.ACTIVE,
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            timezone=timezone,
            status=status,
        )
        db.add(user)
        db.flush()
        db.refresh(user)
        return user

    def get_by_id(self, db: Session, user_id: UUID) -> User | None:
        return db.scalar(select(User).where(User.id == user_id))

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email))

    def list(self, db: Session) -> list[User]:
        return list(db.scalars(select(User).order_by(User.created_at.desc())))

    def update_timezone(self, db: Session, user: User, timezone: str) -> User:
        user.timezone = timezone
        db.flush()
        db.refresh(user)
        return user

    def update_status(self, db: Session, user: User, status: UserStatus) -> User:
        user.status = status
        db.flush()
        db.refresh(user)
        return user
