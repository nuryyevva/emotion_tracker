from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentUserContext, get_current_user, get_db
from app.schemas.emotion import (
    EmotionRecordCreate,
    EmotionRecordList,
    EmotionRecordUpdate,
    EmotionRecordWithStats,
    TodayRecordResponse,
    EmotionRecordResponse,
    DeleteMessageResponse,
)
from app.services.emotion_service import EmotionService

router = APIRouter(prefix="/emotions")


def get_emotion_service(
        db: Annotated[Session, Depends(get_db)],
) -> EmotionService:
    """Dependency provider for EmotionService bound to current DB session."""
    return EmotionService(db)


@router.post("/", response_model=EmotionRecordWithStats, status_code=status.HTTP_201_CREATED)
def create_emotion(
    payload: EmotionRecordCreate,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[EmotionService, Depends(get_emotion_service)],
) -> EmotionRecordWithStats:
    try:
        return service.create_record(user.user_id, payload.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/today", response_model=TodayRecordResponse)
def get_today_emotion(
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[EmotionService, Depends(get_emotion_service)],
) -> TodayRecordResponse:
    return service.get_today_record(user.user_id)


@router.get("/", response_model=EmotionRecordList)
def get_emotions(
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[EmotionService, Depends(get_emotion_service)],
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    limit: int = Query(default=30, ge=1, le=365),
) -> EmotionRecordList:
    today = date.today()
    if end_date is None:
        end_date = today
    if start_date is None:
        start_date = end_date - timedelta(days=29)

    if start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start_date must be <= end_date")

    items = service.get_history(
        user_id=user.user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return EmotionRecordList(
        items=items,
        total=len(items),
        period={"start_date": start_date, "end_date": end_date},
    )


@router.put("/{emotion_id}", response_model=EmotionRecordResponse)
def update_emotion(
    emotion_id: UUID,
    payload: EmotionRecordUpdate,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[EmotionService, Depends(get_emotion_service)],
) -> EmotionRecordResponse:
    try:
        updated = service.update_record(
            user_id=user.user_id,
            record_id=emotion_id,
            data=payload.model_dump(exclude_none=True),
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{emotion_id}", response_model=DeleteMessageResponse)
def delete_emotion(
    emotion_id: UUID,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[EmotionService, Depends(get_emotion_service)],
) -> DeleteMessageResponse:
    deleted = service.delete_record(user.user_id, emotion_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return DeleteMessageResponse(message="Record deleted successfully")