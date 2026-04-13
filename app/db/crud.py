from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EmotionRecord, User, UserStatus


def create_user(session: Session, email: str, password_hash: str, timezone: str, status: UserStatus = UserStatus.ACTIVE) -> User:
    user = User(email=email, password_hash=password_hash, timezone=timezone, status=status)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def list_users(session: Session) -> list[User]:
    return list(session.scalars(select(User).order_by(User.created_at.desc())))


def create_emotion_record(
    session: Session,
    user_id: str,
    record_date: date,
    mood: int,
    anxiety: int,
    fatigue: int,
    sleep_hours: Decimal | None = None,
    note: str | None = None,
) -> EmotionRecord:
    record = EmotionRecord(
        user_id=user_id,
        record_date=record_date,
        mood=mood,
        anxiety=anxiety,
        fatigue=fatigue,
        sleep_hours=sleep_hours,
        note=note,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_emotion_records(session: Session, user_id: str) -> list[EmotionRecord]:
    stmt = select(EmotionRecord).where(EmotionRecord.user_id == user_id).order_by(EmotionRecord.record_date.desc())
    return list(session.scalars(stmt))
