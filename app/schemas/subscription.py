from pydantic import Field
from datetime import datetime
from uuid import UUID
from .common import BaseSchema, UUIDMixin, SubscriptionPlan, SubscriptionStatus

class SubscriptionCreate(BaseSchema):
    plan: SubscriptionPlan = SubscriptionPlan.PRO
    provider: str = "stripe"  # или другой платежный шлюз
    external_payment_id: str | None = None

class SubscriptionResponse(UUIDMixin, BaseSchema):
    user_id: UUID
    plan: SubscriptionPlan
    status: SubscriptionStatus
    started_at: datetime
    expires_at: datetime
    provider: str

class PaymentIntentRequest(BaseSchema):
    plan: SubscriptionPlan
    success_url: str
    cancel_url: str

class PaymentWebhook(BaseSchema):
    provider: str
    event_type: str
    payload: dict
