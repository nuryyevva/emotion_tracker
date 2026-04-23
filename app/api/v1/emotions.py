from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import EmotionRecord
from app.schemas.emotion import EmotionRecordCreate, EmotionRecordList, EmotionRecordResponse

router = APIRouter()


@router.post("/", response_model=EmotionRecordResponse, status_code=status.HTTP_201_CREATED)
def create_emotion(
    payload: EmotionRecordCreate,
    user_id: UUID = Query(...),
    db: Session = Depends(get_db),
) -> EmotionRecordResponse:
    existing = db.scalar(
        select(EmotionRecord).where(
            EmotionRecord.user_id == str(user_id),
            EmotionRecord.record_date == payload.record_date,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Emotion record already exists for this date")

    record = EmotionRecord(
        user_id=str(user_id),
        record_date=payload.record_date,
        mood=payload.mood,
        anxiety=payload.anxiety,
        fatigue=payload.fatigue,
        sleep_hours=Decimal(str(payload.sleep_hours)) if payload.sleep_hours is not None else None,
        note=payload.note,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return EmotionRecordResponse.model_validate(record)


@router.get("/", response_model=EmotionRecordList)
def list_emotions(user_id: UUID = Query(...), db: Session = Depends(get_db)) -> EmotionRecordList:
    records = list(
        db.scalars(
            select(EmotionRecord)
            .where(EmotionRecord.user_id == str(user_id))
            .order_by(EmotionRecord.record_date.desc())
        )
    )

    items = [EmotionRecordResponse.model_validate(record) for record in records]
    if records:
        period = {"start_date": records[-1].record_date, "end_date": records[0].record_date}
    else:
        period = {}
    return EmotionRecordList(items=items, total=len(items), period=period)




from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from uuid import uuid4

router = APIRouter(prefix="/emotions", tags=["Emotions"])


class EmotionResponse(BaseModel):
    id: str
    user_id: str
    emotion_type: str
    intensity: int
    note: Optional[str]
    triggers: Optional[List[str]]
    created_at: datetime
    date: date


class EmotionCreateRequest(BaseModel):
    emotion_type: str
    intensity: int
    note: Optional[str] = None
    triggers: Optional[List[str]] = None
    date: Optional[date] = None


class EmotionUpdateRequest(BaseModel):
    emotion_type: Optional[str] = None
    intensity: Optional[int] = None
    note: Optional[str] = None
    triggers: Optional[List[str]] = None
    date: Optional[date] = None


class EmotionTodayResponse(BaseModel):
    has_emotion: bool
    emotion: Optional[EmotionResponse]
    suggestion: Optional[str]


class EmotionStatsResponse(BaseModel):
    total_entries: int
    average_intensity: float
    most_common_emotion: str
    emotion_distribution: dict
    intensity_trend: List[dict]
    period_days: int


@router.get("/emotions/today", response_model=EmotionTodayResponse)
async def get_emotions_today():
    return EmotionTodayResponse(
        has_emotion=True,
        emotion=EmotionResponse(
            id=str(uuid4()),
            user_id=str(uuid4()),
            emotion_type="happy",
            intensity=7,
            note="Had a great day!",
            triggers=["friends", "sunny_weather"],
            created_at=datetime.now(),
            date=date.today()
        ),
        suggestion="Keep up the positive energy!"
    )


@router.post("/emotions", response_model=EmotionResponse, status_code=status.HTTP_201_CREATED)
async def post_emotions(request: EmotionCreateRequest):
    return EmotionResponse(
        id=str(uuid4()),
        user_id=str(uuid4()),
        emotion_type=request.emotion_type,
        intensity=request.intensity,
        note=request.note,
        triggers=request.triggers,
        created_at=datetime.now(),
        date=request.date or date.today()
    )


@router.put("/emotions/{emotion_id}", response_model=EmotionResponse)
async def put_emotions_emotion_id(emotion_id: str, request: EmotionUpdateRequest):
    return EmotionResponse(
        id=emotion_id,
        user_id=str(uuid4()),
        emotion_type=request.emotion_type or "calm",
        intensity=request.intensity or 5,
        note=request.note,
        triggers=request.triggers,
        created_at=datetime.now(),
        date=request.date or date.today()
    )


@router.delete("/emotions/{emotion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emotions_emotion_id(emotion_id: str):
    return None