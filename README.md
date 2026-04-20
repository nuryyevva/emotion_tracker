# emotion_tracker

## Quick Start

1. Copy `.env.example` to `.env`.
2. Adjust database credentials and `SECRET_KEY`.
3. Run `docker compose up --build`.
4. Open API docs at [http://localhost:8000/docs](http://localhost:8000/docs).
5. Open frontend at [http://localhost:8090](http://localhost:8090).

## Current Architecture

- `app/core/config.py` contains environment-based settings.
- `app/core/database.py` is the shared SQLAlchemy engine and session layer.
- `app/api/main.py` is the FastAPI entrypoint.
- `app/db/models.py` remains the current ORM source of truth for the domain model.

This keeps the existing database model while moving the project closer to a standard `FastAPI + PostgreSQL + Docker` setup.
