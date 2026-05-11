from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUserContext, get_current_user, get_db
from app.schemas.analytics import LastMonthAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics")


def get_analytics_service(
    db: Annotated[Session, Depends(get_db)],
) -> AnalyticsService:
    """Dependency provider for analytics service bound to the current session."""

    return AnalyticsService(db)


@router.get("/last-month", response_model=LastMonthAnalyticsResponse)
def get_last_month_analytics(
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> LastMonthAnalyticsResponse:
    """Return mood, anxiety and fatigue values for the last 30 days."""

    return service.get_last_month(user.user_id)

