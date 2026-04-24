from __future__ import annotations

from datetime import datetime, time
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.schemas.common import NotifyFrequency, UserStatus, enum_values, NotificationChannel

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        Index("ix_users_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", values_callable=enum_values),
        default=UserStatus.ACTIVE,
        server_default=UserStatus.ACTIVE.value,
        nullable=False,
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    settings: Mapped["UserSettings"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    emotion_records: Mapped[list["EmotionRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    hobbies: Mapped[list["UserHobby"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    coping_methods: Mapped[list["UserCopingMethod"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["NotificationLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"
    __table_args__ = (
        CheckConstraint("notify_window_end > notify_window_start", name="chk_user_settings_notify_window"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )
    weekday_wake_up: Mapped[time] = mapped_column(nullable=False)
    weekday_bedtime: Mapped[time] = mapped_column(nullable=False)
    weekend_wake_up: Mapped[time] = mapped_column(nullable=False)
    weekend_bedtime: Mapped[time] = mapped_column(nullable=False)
    notify_channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, name="notify_channel", values_callable=enum_values),
        nullable=False,
        server_default=NotificationChannel.EMAIL.value,
        default=NotificationChannel.EMAIL,
    )
    notify_window_start: Mapped[time] = mapped_column(nullable=False)
    notify_window_end: Mapped[time] = mapped_column(nullable=False)
    notify_frequency: Mapped[NotifyFrequency] = mapped_column(
        Enum(NotifyFrequency, name="notify_frequency", values_callable=enum_values),
        nullable=False,
        server_default=NotifyFrequency.DAILY.value,
        default=NotifyFrequency.DAILY,
    )
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="settings")


class UserHobby(Base):
    __tablename__ = "user_hobbies"
    __table_args__ = (
        UniqueConstraint("user_id", "hobby", name="uq_user_hobbies_user_hobby"),
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
    hobby: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="hobbies")


class UserCopingMethod(Base):
    __tablename__ = "user_coping_methods"
    __table_args__ = (
        UniqueConstraint("user_id", "method", name="uq_user_coping_methods_user_method"),
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
    method: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="coping_methods")
