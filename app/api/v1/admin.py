from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.api.dependencies import get_db, require_admin
from app.services.admin_service import AdminService
from app.schemas.admin import (
    # User schemas
    AdminUserResponse,
    AdminUserList,
    # User settings schemas
    AdminUserSettingsResponse,
    AdminUserSettingsList,
    # Hobby schemas
    AdminHobbyResponse,
    AdminHobbyList,
    # Coping method schemas
    AdminCopingMethodResponse,
    AdminCopingMethodList,
    # Emotion record schemas
    AdminEmotionRecordResponse,
    AdminEmotionRecordList,
    # Notification log schemas
    AdminNotificationLogResponse,
    AdminNotificationLogList,
    # Recommendation schemas
    AdminRecommendationCreate,
    AdminRecommendationResponse,
    AdminRecommendationList,
    # Subscription schemas
    AdminSubscriptionResponse,
    AdminSubscriptionList,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Get admin service instance."""
    return AdminService(db)


# =============================================================================
# USERS ENDPOINTS
# =============================================================================

@router.get("/users", response_model=AdminUserList)
async def get_all_users(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of records to return"),
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get all users with pagination."""
    users = service.list_all_users(skip=skip, limit=limit)
    total = service.count_users()
    return AdminUserList(items=users, total=total)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: UUID,
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get a single user by ID."""
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Delete a user by ID."""
    deleted = service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


# =============================================================================
# USER SETTINGS ENDPOINTS
# =============================================================================

@router.get("/user-settings", response_model=AdminUserSettingsList)
async def get_all_user_settings(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of records to return"),
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get all user settings with pagination."""
    settings = service.list_all_user_settings(skip=skip, limit=limit)
    total = service.count_user_settings()
    return AdminUserSettingsList(items=settings, total=total)


# =============================================================================
# HOBBIES ENDPOINTS
# =============================================================================

@router.get("/hobbies", response_model=AdminHobbyList)
async def get_all_hobbies(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of records to return"),
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get all user hobbies with pagination."""
    hobbies = service.list_all_hobbies(skip=skip, limit=limit)
    total = service.count_hobbies()
    return AdminHobbyList(items=hobbies, total=total)


# =============================================================================
# COPING METHODS ENDPOINTS
# =============================================================================

@router.get("/coping-methods", response_model=AdminCopingMethodList)
async def get_all_coping_methods(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of records to return"),
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get all user coping methods with pagination."""
    methods = service.list_all_coping_methods(skip=skip, limit=limit)
    total = service.count_coping_methods()
    return AdminCopingMethodList(items=methods, total=total)


# =============================================================================
# EMOTION RECORDS ENDPOINTS
# =============================================================================

@router.get("/emotions", response_model=AdminEmotionRecordList)
async def get_all_emotions(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of records to return"),
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get all emotion records with pagination."""
    emotions = service.list_all_emotions(skip=skip, limit=limit)
    total = service.count_emotions()
    return AdminEmotionRecordList(items=emotions, total=total)


# =============================================================================
# NOTIFICATIONS ENDPOINTS
# =============================================================================

@router.get("/notifications", response_model=AdminNotificationLogList)
async def get_all_notifications(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of records to return"),
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get all notification logs with pagination."""
    notifications = service.list_all_notifications(skip=skip, limit=limit)
    total = service.count_notifications()
    return AdminNotificationLogList(items=notifications, total=total)


# =============================================================================
# RECOMMENDATIONS ENDPOINTS
# =============================================================================

@router.post("/recommendations", response_model=AdminRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    request: AdminRecommendationCreate,
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Create a new recommendation."""
    data = request.model_dump()
    recommendation = service.create_recommendation(data)
    return recommendation


@router.get("/recommendations", response_model=AdminRecommendationList)
async def get_recommendations(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get all recommendations with pagination and optional filter."""
    recommendations = service.list_all_recommendations(skip=skip, limit=limit, is_active=is_active)
    total = service.count_recommendations(is_active=is_active)
    return AdminRecommendationList(items=recommendations, total=total)


@router.get("/recommendations/{rec_id}", response_model=AdminRecommendationResponse)
async def get_recommendation(
    rec_id: UUID,
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get a single recommendation by ID."""
    recommendation = service.get_recommendation_by_id(rec_id)
    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return recommendation


@router.delete("/recommendations/{rec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    rec_id: UUID,
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Delete a recommendation by ID."""
    deleted = service.delete_recommendation(rec_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")


# =============================================================================
# SUBSCRIPTIONS ENDPOINTS
# =============================================================================

@router.get("/subscriptions", response_model=AdminSubscriptionList)
async def get_all_subscriptions(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of records to return"),
    service: AdminService = Depends(get_admin_service),
    _ = Depends(require_admin),
):
    """Get all subscriptions with pagination."""
    subscriptions = service.list_all_subscriptions(skip=skip, limit=limit)
    total = service.count_subscriptions()
    return AdminSubscriptionList(items=subscriptions, total=total)