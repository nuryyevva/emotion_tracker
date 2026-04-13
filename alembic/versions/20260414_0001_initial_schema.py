"""Initial schema

Revision ID: 20260414_0001
Revises:
Create Date: 2026-04-14 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260414_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_status = postgresql.ENUM("active", "blocked", "deleted", name="user_status", create_type=False)
    notify_channel = postgresql.ENUM("email", "telegram", "both", name="notify_channel", create_type=False)
    notify_frequency = postgresql.ENUM("daily", "weekly", "smart", name="notify_frequency", create_type=False)
    subscription_status = postgresql.ENUM("active", "expired", "canceled", "trial", name="subscription_status", create_type=False)
    delivery_status = postgresql.ENUM("queued", "sent", "failed", "read", name="delivery_status", create_type=False)

    bind = op.get_bind()
    postgresql.ENUM("active", "blocked", "deleted", name="user_status").create(bind, checkfirst=True)
    postgresql.ENUM("email", "telegram", "both", name="notify_channel").create(bind, checkfirst=True)
    postgresql.ENUM("daily", "weekly", "smart", name="notify_frequency").create(bind, checkfirst=True)
    postgresql.ENUM("active", "expired", "canceled", "trial", name="subscription_status").create(bind, checkfirst=True)
    postgresql.ENUM("queued", "sent", "failed", "read", name="delivery_status").create(bind, checkfirst=True)

    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trigger_type", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recommendations_trigger_type", "recommendations", ["trigger_type"])
    op.create_index("ix_recommendations_category", "recommendations", ["category"])
    op.create_index("ix_recommendations_is_active", "recommendations", ["is_active"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("timezone", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("status", user_status, nullable=False, server_default="active"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_status", "users", ["status"])

    op.create_table(
        "emotion_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("mood", sa.Integer(), nullable=False),
        sa.Column("anxiety", sa.Integer(), nullable=False),
        sa.Column("fatigue", sa.Integer(), nullable=False),
        sa.Column("sleep_hours", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("anxiety BETWEEN 1 AND 10", name="chk_emotion_records_anxiety"),
        sa.CheckConstraint("fatigue BETWEEN 1 AND 10", name="chk_emotion_records_fatigue"),
        sa.CheckConstraint("mood BETWEEN 1 AND 10", name="chk_emotion_records_mood"),
        sa.CheckConstraint("sleep_hours IS NULL OR sleep_hours BETWEEN 0 AND 24", name="chk_emotion_records_sleep_hours"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "record_date", name="uq_emotion_records_user_date"),
    )
    op.create_index("ix_emotion_records_user_id", "emotion_records", ["user_id"])
    op.create_index("ix_emotion_records_record_date", "emotion_records", ["record_date"])

    op.create_table(
        "notification_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("trigger_type", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("delivery_status", delivery_status, nullable=False, server_default="queued"),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_log_delivery_status", "notification_log", ["delivery_status"])
    op.create_index("ix_notification_log_sent_at", "notification_log", ["sent_at"])
    op.create_index("ix_notification_log_user_id", "notification_log", ["user_id"])

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan", sa.String(length=100), nullable=False),
        sa.Column("status", subscription_status, nullable=False, server_default="trial"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider", sa.String(length=100), nullable=True),
        sa.Column("external_payment_id", sa.String(length=255), nullable=True),
        sa.CheckConstraint("expires_at IS NULL OR expires_at >= started_at", name="chk_subscriptions_period"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_payment_id"),
    )
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])

    op.create_table(
        "user_coping_methods",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("method", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "method", name="uq_user_coping_methods_user_method"),
    )
    op.create_index("ix_user_coping_methods_user_id", "user_coping_methods", ["user_id"])

    op.create_table(
        "user_hobbies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hobby", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "hobby", name="uq_user_hobbies_user_hobby"),
    )
    op.create_index("ix_user_hobbies_user_id", "user_hobbies", ["user_id"])

    op.create_table(
        "user_settings",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weekday_wake_up", sa.Time(), nullable=False),
        sa.Column("weekday_bedtime", sa.Time(), nullable=False),
        sa.Column("weekend_wake_up", sa.Time(), nullable=False),
        sa.Column("weekend_bedtime", sa.Time(), nullable=False),
        sa.Column("notify_channel", notify_channel, nullable=False, server_default="email"),
        sa.Column("notify_window_start", sa.Time(), nullable=False),
        sa.Column("notify_window_end", sa.Time(), nullable=False),
        sa.Column("notify_frequency", notify_frequency, nullable=False, server_default="daily"),
        sa.Column("reminders_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("notify_window_end > notify_window_start", name="chk_user_settings_notify_window"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_table("user_settings")
    op.drop_index("ix_user_hobbies_user_id", table_name="user_hobbies")
    op.drop_table("user_hobbies")
    op.drop_index("ix_user_coping_methods_user_id", table_name="user_coping_methods")
    op.drop_table("user_coping_methods")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_status", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index("ix_notification_log_user_id", table_name="notification_log")
    op.drop_index("ix_notification_log_sent_at", table_name="notification_log")
    op.drop_index("ix_notification_log_delivery_status", table_name="notification_log")
    op.drop_table("notification_log")
    op.drop_index("ix_emotion_records_record_date", table_name="emotion_records")
    op.drop_index("ix_emotion_records_user_id", table_name="emotion_records")
    op.drop_table("emotion_records")
    op.drop_index("ix_users_status", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_recommendations_is_active", table_name="recommendations")
    op.drop_index("ix_recommendations_category", table_name="recommendations")
    op.drop_index("ix_recommendations_trigger_type", table_name="recommendations")
    op.drop_table("recommendations")

    postgresql.ENUM(name="delivery_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="subscription_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="notify_frequency").drop(bind, checkfirst=True)
    postgresql.ENUM(name="notify_channel").drop(bind, checkfirst=True)
    postgresql.ENUM(name="user_status").drop(bind, checkfirst=True)
