from __future__ import annotations

import enum


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


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_cls]
