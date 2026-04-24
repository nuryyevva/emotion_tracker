from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.common import UserStatus
from app.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository responsible for reading and mutating ``User`` entities."""

    def __init__(self, db: Session):
        super().__init__(db)

    model = User

    def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by UUID.

        This is kept as an explicit domain method even though ``BaseRepository``
        already exposes ``get`` because the service layer works with domain names
        like ``get_by_id``.
        """

        return self.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        """Return a user by email or ``None`` if such account does not exist."""

        return self.db.scalar(select(User).where(User.email == email))

    def list(self) -> list[User]:
        """Return all users ordered from newest to oldest."""

        return list(self.db.scalars(select(User).order_by(User.created_at.desc())))

    def update_timezone(self, user: User, timezone: str) -> User:
        """Update the user's timezone and return the refreshed entity."""

        user.timezone = timezone
        self.db.flush()
        self.db.refresh(user)
        return user

    def update_status(self, user: User, status: UserStatus) -> User:
        """Update the account status, for example ``active`` or ``blocked``."""

        user.status = status
        self.db.flush()
        self.db.refresh(user)
        return user
