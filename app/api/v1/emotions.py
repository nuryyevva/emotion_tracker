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
