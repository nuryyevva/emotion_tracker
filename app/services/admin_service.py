"""
Admin service for managing all entities in the system.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories import (
    UserRepository,
    UserSettingsRepository,
    UserHobbyRepository,
    UserCopingMethodRepository,
    EmotionRepository,
    NotificationRepository,
    RecommendationRepository,
    SubscriptionRepository,
)
from app.models import (
    User,
    UserSettings,
    UserHobby,
    UserCopingMethod,
    EmotionRecord,
    NotificationLog,
    Recommendation,
    Subscription,
)


class AdminService:
    """Service for admin operations across all entities."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.settings_repo = UserSettingsRepository(db)
        self.hobby_repo = UserHobbyRepository(db)
        self.coping_repo = UserCopingMethodRepository(db)
        self.emotion_repo = EmotionRepository(db)
        self.notification_repo = NotificationRepository(db)
        self.recommendation_repo = RecommendationRepository(db)
        self.subscription_repo = SubscriptionRepository(db)

    # ==================== Users ====================

    def list_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Return all users with pagination."""
        return self.user_repo.get_multi(skip=skip, limit=limit, order_by=User.created_at.desc())

    def count_users(self) -> int:
        """Return total number of users."""
        return self.user_repo.count()

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a single user by ID."""
        return self.user_repo.get_by_id(user_id)

    def delete_user(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        result = self.user_repo.remove(id=user_id)
        return result is not None

    # ==================== User Settings ====================

    def list_all_user_settings(self, skip: int = 0, limit: int = 100) -> List[UserSettings]:
        """Return all user settings with pagination."""
        return self.settings_repo.get_multi(skip=skip, limit=limit)

    def count_user_settings(self) -> int:
        """Return total number of user settings."""
        return self.settings_repo.count()

    # ==================== User Hobbies ====================

    def list_all_hobbies(self, skip: int = 0, limit: int = 100) -> List[UserHobby]:
        """Return all user hobbies with pagination."""
        return self.hobby_repo.get_multi(skip=skip, limit=limit, order_by=UserHobby.created_at.desc())

    def count_hobbies(self) -> int:
        """Return total number of hobbies."""
        return self.hobby_repo.count()

    # ==================== User Coping Methods ====================

    def list_all_coping_methods(self, skip: int = 0, limit: int = 100) -> List[UserCopingMethod]:
        """Return all user coping methods with pagination."""
        return self.coping_repo.get_multi(skip=skip, limit=limit, order_by=UserCopingMethod.created_at.desc())

    def count_coping_methods(self) -> int:
        """Return total number of coping methods."""
        return self.coping_repo.count()

    # ==================== Emotion Records ====================

    def list_all_emotions(self, skip: int = 0, limit: int = 100) -> List[EmotionRecord]:
        """Return all emotion records with pagination."""
        return self.emotion_repo.get_multi(skip=skip, limit=limit, order_by=EmotionRecord.record_date.desc())

    def count_emotions(self) -> int:
        """Return total number of emotion records."""
        return self.emotion_repo.count()

    # ==================== Notifications ====================

    def list_all_notifications(self, skip: int = 0, limit: int = 100) -> List[NotificationLog]:
        """Return all notification logs with pagination."""
        return self.notification_repo.get_multi(skip=skip, limit=limit, order_by=NotificationLog.sent_at.desc())

    def count_notifications(self) -> int:
        """Return total number of notifications."""
        return self.notification_repo.count()

    # ==================== Recommendations ====================

    def list_all_recommendations(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[Recommendation]:
        """Return all recommendations with pagination and optional filter."""
        if is_active is None:
            return self.recommendation_repo.get_multi(skip=skip, limit=limit, order_by=Recommendation.priority.desc())
        
        from sqlalchemy import select
        stmt = select(Recommendation).where(Recommendation.is_active == is_active).order_by(Recommendation.priority.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def count_recommendations(self, is_active: Optional[bool] = None) -> int:
        """Return total number of recommendations."""
        if is_active is None:
            return self.recommendation_repo.count()
        return self.recommendation_repo.count(filter_by={"is_active": is_active})

    def create_recommendation(self, data: Dict[str, Any]) -> Recommendation:
        """Create a new recommendation."""
        return self.recommendation_repo.create(obj_in=data)

    def get_recommendation_by_id(self, rec_id: UUID) -> Optional[Recommendation]:
        """Get a recommendation by ID."""
        return self.recommendation_repo.get(rec_id)

    def delete_recommendation(self, rec_id: UUID) -> bool:
        """Delete a recommendation by ID."""
        result = self.recommendation_repo.remove(id=rec_id)
        return result is not None

    # ==================== Subscriptions ====================

    def list_all_subscriptions(self, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """Return all subscriptions with pagination."""
        return self.subscription_repo.get_multi(skip=skip, limit=limit, order_by=Subscription.started_at.desc())

    def count_subscriptions(self) -> int:
        """Return total number of subscriptions."""
        return self.subscription_repo.count()
