from __future__ import annotations

import os
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base

DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/emotion_tracker"


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


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_database_url()
    if url.startswith("postgresql+psycopg"):
        configure_postgres_client()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, echo=False, future=True, connect_args=connect_args)


def get_session(database_url: str | None = None) -> Session:
    engine = get_engine(database_url)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return session_factory()


def create_tables(database_url: str | None = None) -> None:
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)


def create_database(database_url: str | None = None) -> None:
    url = database_url or get_database_url()
    if url.startswith("sqlite"):
        return

    configure_postgres_client()
    import psycopg

    parsed = urlparse(url.replace("+psycopg", ""))
    db_name = parsed.path.lstrip("/")
    admin_db_url = parsed._replace(path="/postgres").geturl()

    with psycopg.connect(admin_db_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone() is not None
            if not exists:
                cur.execute(f'CREATE DATABASE "{db_name}"')
