from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserStatus
from app.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository responsible for reading and mutating ``User`` entities."""

    model = User

    def create(
        self,
        db: Session,
        *,
        email: str,
        password_hash: str,
        timezone: str,
        status: UserStatus = UserStatus.ACTIVE,
    ) -> User:
        """Create a new user with the minimal required account fields.

        Args:
            db: Active SQLAlchemy session.
            email: Unique login email.
            password_hash: Already hashed password value.
            timezone: User timezone string used by reminders and date logic.
            status: Initial user status. Defaults to ``active``.
        """

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
        """Return a user by UUID.

        This is kept as an explicit domain method even though ``BaseRepository``
        already exposes ``get`` because the service layer works with domain names
        like ``get_by_id``.
        """

        return self.get(db, user_id)

    def get_by_email(self, db: Session, email: str) -> User | None:
        """Return a user by email or ``None`` if such account does not exist."""

        return db.scalar(select(User).where(User.email == email))

    def list(self, db: Session) -> list[User]:
        """Return all users ordered from newest to oldest."""

        return list(db.scalars(select(User).order_by(User.created_at.desc())))

    def update_timezone(self, db: Session, user: User, timezone: str) -> User:
        """Update the user's timezone and return the refreshed entity."""

        user.timezone = timezone
        db.flush()
        db.refresh(user)
        return user

    def update_status(self, db: Session, user: User, status: UserStatus) -> User:
        """Update the account status, for example ``active`` or ``blocked``."""

        user.status = status
        db.flush()
        db.refresh(user)
        return user
