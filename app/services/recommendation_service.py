"""
Сервис рекомендаций
"""
from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..repositories.recommendation_repo import RecommendationRepository
from ..repositories.notification_repo import NotificationRepository
from ..schemas.recommendation import RecommendationTemplate
from app.utils.recommendations_engine import select_recommendation


class RecommendationService:
    """Сервис для работы с рекомендациями"""

    def __init__(self, db: Session):
        """
        Инициализация сервиса рекомендаций

        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.repo = RecommendationRepository(db)
        self.notif_repo = NotificationRepository(db)

    def get_recommendation(
            self,
            user_id: UUID,
            trigger_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получение рекомендации для пользователя на основе триггера

        Args:
            user_id: ID пользователя
            trigger_type: Тип триггера

        Returns:
            dict[str, Any] | None: Рекомендация или None
        """
        # Get candidates
        candidates = self.repo.get_by_trigger_type(trigger_type=trigger_type)
        if not candidates:
            return None

        # Get recent IDs (rotation)
        recent_logs = self.notif_repo.get_recent_by_trigger(user_id=user_id, trigger_type=trigger_type, days=7)
        recent_ids = [log.recommendation_id for log in recent_logs if log.recommendation_id]

        # Select
        rec_dict = [{"id": c.id, "message": c.message, "priority": c.priority} for c in candidates]
        selected = select_recommendation(rec_dict, recent_ids, context={"hour": datetime.now().hour})

        return selected

    def get_all_active(
            self,
            trigger_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получение всех активных рекомендаций

        Args:
            trigger_type: Тип триггера (опционально)

        Returns:
            list[dict[str, Any]]: Список активных рекомендаций
        """
        if trigger_type:
            recs = self.repo.get_by_trigger_type(trigger_type=trigger_type)
        else:
            recs = self.repo.get_multi(limit=100)  # Base repo method

        return [
            {"id": r.id, "trigger_type": r.trigger_type, "category": r.category, "message": r.message,
             "priority": r.priority}
            for r in recs
        ]
