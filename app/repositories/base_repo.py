from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic repository with reusable CRUD helpers for SQLAlchemy models.

    Concrete repositories inherit from this class and define the ``model``
    attribute. This keeps the common operations in one place and lets the
    domain-specific repositories focus only on custom queries.
    """

    model: type[ModelType]

    def __init__(self, db: Session):
        """Initialize repository with database session.

        Args:
            db: Active SQLAlchemy session.
        """
        self.db = db

    def get(self, id: UUID) -> ModelType | None:
        """Return a single entity by primary key or ``None`` if it does not exist.

        Important:
            This helper expects the primary key value in its native Python type.
            For the current project that means ``UUID`` for all main domain
            entities. Passing a plain string UUID can break at the SQLAlchemy
            type-processing stage instead of simply returning ``None``.
        """

        return self.db.get(self.model, id)

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Any | None = None,
    ) -> list[ModelType]:
        """Return a paginated list of entities.

        Args:
            skip: Number of rows to skip from the beginning of the result set.
            limit: Maximum number of rows to return.
            order_by: Optional SQLAlchemy column/expression for sorting.

        Returns:
            A list of model instances.
        """

        stmt = select(self.model).offset(skip).limit(limit)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        return list(self.db.scalars(stmt))

    def create(self, *, obj_in: dict[str, Any]) -> ModelType:
        """Create and return a new entity from a plain dictionary of field values."""

        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: ModelType, obj_in: dict[str, Any] | Any) -> ModelType:
        """Update an existing entity with values from a dict or Pydantic object.

        The method intentionally performs a shallow field-by-field update because
        repositories in this project mostly work with flat ORM models.
        """

        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, *, id: UUID) -> ModelType | None:
        """Delete an entity by primary key and return the deleted object if found.

        Important:
            The ``id`` argument should be passed in the exact Python type used by
            the ORM model primary key. In this project it is typically ``UUID``.
        """

        db_obj = self.get(id)
        if db_obj is None:
            return None
        self.db.delete(db_obj)
        self.db.flush()
        return db_obj

    def count(self, *, filter_by: dict[str, Any] | None = None) -> int:
        """Return the number of entities, optionally filtered by exact field values."""

        stmt = select(func.count()).select_from(self.model)
        if filter_by:
            stmt = stmt.filter_by(**filter_by)
        return int(self.db.scalar(stmt) or 0)
