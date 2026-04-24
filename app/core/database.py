"""
Database Configuration

SQLAlchemy engine, session factory, and base model.
Based on Database Diagram from System Analysis.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, declared_attr

from app.core.config import settings

# =============================================================================
# ENGINE
# =============================================================================


def configure_postgres_client() -> None:
    if os.name != "nt":
        return

    candidate_dirs = [
        r"C:\Program Files\PostgreSQL\18\bin",
        r"C:\Program Files\PostgreSQL\17\bin",
        r"C:\Program Files\PostgreSQL\16\bin",
    ]

    for directory in candidate_dirs:
        if os.path.exists(directory):
            os.environ["PATH"] = directory + os.pathsep + os.environ.get("PATH", "")
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(directory)
            break


if settings.DATABASE_URL.startswith("postgresql+psycopg"):
    configure_postgres_client()


engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Enable connection health checks
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# =============================================================================
# SESSION
# =============================================================================


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


# =============================================================================
# BASE MODEL
# =============================================================================


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Uses tablename convention from class name.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Convert CamelCase class name to snake_case table name."""
        return cls.__name__.lower()

    id: any  # Placeholder, actual ID defined in models


# =============================================================================
# DEPENDENCY
# =============================================================================


def get_db():
    """
    Database session dependency.
    Used in app/api/v1/deps.py
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
