from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

router = APIRouter(prefix="/admin", tags=["Admin"])


class RecommendationCreateRequest(BaseModel):
    title: str
    description: str
    recommendation_type: str
    target_emotions: Optional[List[str]] = None
    action_url: Optional[str] = None
    priority: int = 0
    is_active: bool = True


class RecommendationResponse(BaseModel):
    id: str
    title: str
    description: str
    recommendation_type: str
    target_emotions: Optional[List[str]]
    action_url: Optional[str]
    priority: int
    is_active: bool
    created_at: datetime


class RecommendationListResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    total: int


@router.post("/recommendations", response_model=RecommendationResponse, status_code=201)
async def post_recommendations(request: RecommendationCreateRequest):
    return RecommendationResponse(
        id=str(uuid4()),
        title=request.title,
        description=request.description,
        recommendation_type=request.recommendation_type,
        target_emotions=request.target_emotions,
        action_url=request.action_url,
        priority=request.priority,
        is_active=request.is_active,
        created_at=datetime.now()
    )


@router.get("/recommendations", response_model=RecommendationListResponse)
async def get_recommendations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    is_active: Optional[bool] = None
):
    return RecommendationListResponse(
        recommendations=[],
        total=0
    )