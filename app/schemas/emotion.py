from pydantic import Field, field_validator
from datetime import date
from uuid import UUID
from .common import BaseSchema, UUIDMixin, TimestampMixin

class EmotionRecordBase(BaseSchema):
    mood: int = Field(..., ge=1, le=10, description="Настроение 1-10")
    anxiety: int = Field(..., ge=1, le=10, description="Тревожность 1-10")
    fatigue: int = Field(..., ge=1, le=10, description="Усталость 1-10")
    sleep_hours: float | None = Field(None, ge=0, le=24, description="Часы сна")
    note: str | None = Field(None, max_length=500, description="Заметка до 500 символов")
    record_date: date

class EmotionRecordCreate(EmotionRecordBase):
    pass

class EmotionRecordUpdate(BaseSchema):
    mood: int | None = Field(None, ge=1, le=10)
    anxiety: int | None = Field(None, ge=1, le=10)
    fatigue: int | None = Field(None, ge=1, le=10)
    sleep_hours: float | None = Field(None, ge=0, le=24)
    note: str | None = Field(None, max_length=500)

class EmotionRecordResponse(EmotionRecordBase, UUIDMixin, TimestampMixin):
    user_id: UUID

class EmotionRecordList(BaseSchema):
    items: list[EmotionRecordResponse]
    total: int
