"""
Analytics API endpoints.
"""
from datetime import date, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, CurrentUserContext
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import WeeklyAveragesResponse, WeekdayAveragesListResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(
        db: Annotated[Session, Depends(get_db)],
) -> AnalyticsService:
    """Dependency provider for AnalyticsService."""
    return AnalyticsService(db)


@router.get("/weekly-averages", response_model=WeeklyAveragesResponse)
def get_weekly_averages(
        user: Annotated[CurrentUserContext, Depends(get_current_user)],
        service: Annotated[AnalyticsService, Depends(get_analytics_service)],
        start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
) -> WeeklyAveragesResponse:
    """
    Get daily average values for emotions over a period.

    Returns JSON in format:
    {
        "26.04.2026": {"mood": 6.2, "anxiety": 5.5, "fatigue": 6.0},
        "25.04.2026": {"mood": 6.8, "anxiety": 4.9, "fatigue": 5.5}
    }
    """
    today = date.today()

    if end_date is None:
        end_date = today
    if start_date is None:
        start_date = end_date - timedelta(days=29)  # Default to last 30 days

    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be less than or equal to end_date"
        )

    period_days = (end_date - start_date).days + 1
    if period_days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period cannot exceed 365 days"
        )

    return service.get_daily_averages(
        user_id=user.user_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/weekday-averages", response_model=WeekdayAveragesListResponse)
def get_weekday_averages(
        user: Annotated[CurrentUserContext, Depends(get_current_user)],
        service: Annotated[AnalyticsService, Depends(get_analytics_service)],
        start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
) -> WeekdayAveragesListResponse:
    """
    Get average emotion values grouped by day of week.

    Returns average mood, anxiety, and fatigue for each weekday
    (Monday through Sunday) based on data from the specified period.
    """
    today = date.today()

    if end_date is None:
        end_date = today
    if start_date is None:
        start_date = end_date - timedelta(days=89)  # Default to last 90 days

    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be less than or equal to end_date"
        )

    return service.get_weekday_averages(
        user_id=user.user_id,
        start_date=start_date,
        end_date=end_date,
    )