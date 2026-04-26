# emotion_tracker

## Quick Start

1. Copy `.env.example` to `.env`.
2. Adjust database credentials and `SECRET_KEY`.
3. Run `docker compose up --build`.
4. Open API docs at [http://localhost:8000/docs](http://localhost:8000/docs).
5. Open frontend at [http://localhost:8090](http://localhost:8090).

## Alembic migrations

- The project keeps migration files in `alembic/versions`.
- Alembic uses `ALEMBIC_DATABASE_URL` when set, otherwise falls back to `DATABASE_URL`.
- If you run Alembic from your host shell, use `localhost` in `ALEMBIC_DATABASE_URL`.
- Basic commands:
  - `poetry run alembic revision --autogenerate -m "describe_change"`
  - `poetry run alembic upgrade head`
  - `poetry run alembic downgrade -1`

## Current Architecture

- `app/core/config.py` contains environment-based settings.
- `app/core/database.py` is the shared SQLAlchemy engine and session layer.
- `app/api/main.py` is the FastAPI entrypoint.
