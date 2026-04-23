from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmotionRecord(Base):
    __tablename__ = "emotion_records"
    __table_args__ = (
        UniqueConstraint("user_id", "record_date", name="uq_emotion_records_user_date"),
        CheckConstraint("mood BETWEEN 1 AND 10", name="chk_emotion_records_mood"),
        CheckConstraint("anxiety BETWEEN 1 AND 10", name="chk_emotion_records_anxiety"),
        CheckConstraint("fatigue BETWEEN 1 AND 10", name="chk_emotion_records_fatigue"),
        CheckConstraint("sleep_hours IS NULL OR sleep_hours BETWEEN 0 AND 24", name="chk_emotion_records_sleep_hours"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    mood: Mapped[int] = mapped_column(nullable=False)
    anxiety: Mapped[int] = mapped_column(nullable=False)
    fatigue: Mapped[int] = mapped_column(nullable=False)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="emotion_records")
