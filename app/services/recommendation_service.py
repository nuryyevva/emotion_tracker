"""
Сервис рекомендаций
"""
from uuid import UUID
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from ..repositories.recommendation_repo import RecommendationRepository
from ..repositories.notification_repo import NotificationRepository
from ..schemas.recommendation import RecommendationTemplate


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
        self.notif_service = NotificationRepository(db)

    def _to_dict(self, recommendation) -> Dict[str, Any]:
        """Конвертирует ORM модель в словарь"""
        return {
            "id": recommendation.id,
            "trigger_type": recommendation.trigger_type,
            "category": recommendation.category,
            "message": recommendation.message,
            "priority": recommendation.priority,
            "is_active": recommendation.is_active
        }

    def _to_response(self, recommendation) -> RecommendationTemplate:
        """Конвертирует ORM модель в Response схему"""
        return RecommendationTemplate(
            id=recommendation.id,
            trigger_type=recommendation.trigger_type,
            category=recommendation.category,
            message=recommendation.message,
            priority=recommendation.priority,
            is_active=recommendation.is_active,
            created_at=recommendation.created_at,
            updated_at=recommendation.updated_at
        )

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
        # Получение недавних уведомлений этого типа
        recent = self.notif_service.get_recent_by_trigger(
            user_id=user_id,
            trigger_type=trigger_type,
            days=7
        )
        exclude_ids = [n.recommendation_id for n in recent if n.recommendation_id]

        # Получение случайной активной рекомендации
        recommendation = self.repo.get_random_active(
            trigger_type=trigger_type,
            exclude_ids=exclude_ids if exclude_ids else None
        )

        if recommendation:
            return self._to_dict(recommendation)

        return None

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
            recommendations = self.repo.get_by_trigger_type(
                trigger_type=trigger_type,
                is_active=True
            )
        else:
            # Получение всех активных по всем типам
            all_triggers = ["fatigue_high", "anxiety_high", "mood_low", "mood_improvement", "sleep_deviation"]
            recommendations = []
            for t in all_triggers:
                recommendations.extend(self.repo.get_by_trigger_type(trigger_type=t, is_active=True))

        return [self._to_dict(r) for r in recommendations]