from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EmotionRecord


class EmotionRecordRepository:
    def create(
        self,
        db: Session,
        *,
        user_id: UUID,
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
        db.add(record)
        db.flush()
        db.refresh(record)
        return record

    def get_by_user_and_date(self, db: Session, user_id: UUID, record_date: date) -> EmotionRecord | None:
        stmt = select(EmotionRecord).where(
            EmotionRecord.user_id == user_id,
            EmotionRecord.record_date == record_date,
        )
        return db.scalar(stmt)

    def list_by_user(self, db: Session, user_id: UUID) -> list[EmotionRecord]:
        stmt = (
            select(EmotionRecord)
            .where(EmotionRecord.user_id == user_id)
            .order_by(EmotionRecord.record_date.desc())
        )
        return list(db.scalars(stmt))
