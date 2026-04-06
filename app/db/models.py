from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def uuid_str() -> str:
    return str(uuid.uuid4())


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"


class NotifyChannel(str, enum.Enum):
    EMAIL = "email"
    TELEGRAM = "telegram"
    BOTH = "both"


class NotifyFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SMART = "smart"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"
    TRIAL = "trial"


class DeliveryStatus(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    settings: Mapped["UserSettings"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    emotion_records: Mapped[list["EmotionRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    hobbies: Mapped[list["UserHobby"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    coping_methods: Mapped[list["UserCopingMethod"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["NotificationLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), primary_key=True)
    weekday_wake_up: Mapped[time | None] = mapped_column(nullable=True)
    weekday_bedtime: Mapped[time | None] = mapped_column(nullable=True)
    weekend_wake_up: Mapped[time | None] = mapped_column(nullable=True)
    weekend_bedtime: Mapped[time | None] = mapped_column(nullable=True)
    notify_channel: Mapped[NotifyChannel | None] = mapped_column(Enum(NotifyChannel), nullable=True)
    notify_window_start: Mapped[time | None] = mapped_column(nullable=True)
    notify_window_end: Mapped[time | None] = mapped_column(nullable=True)
    notify_frequency: Mapped[NotifyFrequency | None] = mapped_column(Enum(NotifyFrequency), nullable=True)
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="settings")


class EmotionRecord(Base):
    __tablename__ = "emotion_records"
    __table_args__ = (UniqueConstraint("user_id", "record_date", name="uq_emotion_records_user_date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    mood: Mapped[int] = mapped_column(nullable=False)
    anxiety: Mapped[int] = mapped_column(nullable=False)
    fatigue: Mapped[int] = mapped_column(nullable=False)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="emotion_records")


class UserHobby(Base):
    __tablename__ = "user_hobbies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    hobby: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="hobbies")


class UserCopingMethod(Base):
    __tablename__ = "user_coping_methods"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    method: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="coping_methods")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    trigger_type: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    notifications: Mapped[list["NotificationLog"]] = relationship(back_populates="recommendation")


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    recommendation_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("recommendations.id"), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.QUEUED, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="notifications")
    recommendation: Mapped["Recommendation | None"] = relationship(back_populates="notifications")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    plan: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="subscriptions")
