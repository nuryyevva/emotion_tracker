"""
Сервис пользователей
"""
from uuid import UUID
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.schemas.common import UserStatus
from app.repositories import UserRepository, UserHobbyRepository, UserSettingsRepository, UserCopingMethodRepository
from app.schemas.user import (
    UserResponse,
    UserSettingsResponse,
    HobbyResponse,
    CopingMethodResponse,
)
from app.core.exceptions import ResourceNotFoundException


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db: Session):
        """
        Инициализация сервиса пользователей

        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.settings_repo = UserSettingsRepository(db)
        self.hobby_repo = UserHobbyRepository(db)
        self.coping_repo = UserCopingMethodRepository(db)

    def get_profile(self, user_id: UUID) -> UserResponse:
        """
        Получение профиля пользователя

        Args:
            user_id: ID пользователя

        Returns:
            UserResponse: Объект с данными профиля
        """
        user = self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise ResourceNotFoundException("User")

        return UserResponse(
            id=user.id,
            email=user.email,
            timezone=user.timezone,
            status=user.status.value if hasattr(user.status, 'value') else str(user.status),
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    def update_profile(self, user_id: UUID, update: Dict[str, Any]) -> UserResponse:
        """
        Обновление профиля пользователя.

        Args:
            user_id: ID пользователя
            update: Поля для обновления профиля

        Returns:
            UserResponse: Обновленный профиль пользователя
        """
        user = self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise ResourceNotFoundException("User")

        timezone = update.get("timezone")
        if timezone is not None:
            self.user_repo.update_timezone(user=user, timezone=timezone)

        return self.get_profile(user_id)

    def soft_delete_profile(self, user_id: UUID) -> None:
        """
        Мягкое удаление пользователя (смена статуса).

        Args:
            user_id: ID пользователя
        """
        user = self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise ResourceNotFoundException("User")

        self.user_repo.update_status(user=user, status=UserStatus.DELETED)

    def create_default_settings(self, user_id: UUID) -> None:
        """
        Создание настроек по умолчанию для нового пользователя

        Args:
            user_id: ID пользователя
        """
        self.settings_repo.create_default(user_id=user_id)

    def get_settings(self, user_id: UUID) -> UserSettingsResponse:
        """
        Получение настроек пользователя

        Args:
            user_id: ID пользователя

        Returns:
            UserSettingsResponse: Объект с настройками
        """
        settings = self.settings_repo.get_by_user(user_id=user_id)
        if not settings:
            settings = self.settings_repo.create_default(user_id=user_id)

        hobbies = self.hobby_repo.list_by_user(user_id=user_id)
        coping_methods = self.coping_repo.list_by_user(user_id=user_id)

        return UserSettingsResponse(
            user_id=user_id,
            weekday_wake_up=settings.weekday_wake_up,
            weekday_bedtime=settings.weekday_bedtime,
            weekend_wake_up=settings.weekend_wake_up,
            weekend_bedtime=settings.weekend_bedtime,
            notify_channel=settings.notify_channel,
            notify_window_start=settings.notify_window_start,
            notify_window_end=settings.notify_window_end,
            notify_frequency=settings.notify_frequency.value if hasattr(settings.notify_frequency, 'value') else str(
                settings.notify_frequency),
            reminders_enabled=settings.reminders_enabled,
            updated_at=settings.updated_at,
            hobbies=[h.hobby for h in hobbies],
            coping_methods=[c.method for c in coping_methods]
        )

    def update_settings(self, user_id: UUID, update: Dict[str, Any]) -> UserSettingsResponse:
        """
        Обновление настроек пользователя

        Args:
            user_id: ID пользователя
            update: Словарь с обновляемыми полями

        Returns:
            UserSettingsResponse: Обновленный объект с настройками
        """
        settings = self.settings_repo.get_by_user(user_id)
        if not settings:
            settings = self.settings_repo.create_default(user_id=user_id)

        self.settings_repo.update(
            settings=settings,
            weekday_wake_up=update.get("weekday_wake_up"),
            weekday_bedtime=update.get("weekday_bedtime"),
            weekend_wake_up=update.get("weekend_wake_up"),
            weekend_bedtime=update.get("weekend_bedtime"),
            channel=update.get("notify_channel"),
            window_start=update.get("notify_window_start"),
            window_end=update.get("notify_window_end"),
            frequency=update.get("notify_frequency"),
            enabled=update.get("reminders_enabled"),
        )

        return self.get_settings(user_id)

    def add_hobby(self, user_id: UUID, hobby: str) -> HobbyResponse:
        """
        Добавление хобби пользователю

        Args:
            user_id: ID пользователя
            hobby: Название хобби

        Returns:
            HobbyResponse: Объект с данными хобби
        """
        existing = self.hobby_repo.get_by_user_and_name(user_id=user_id, hobby=hobby)
        if existing:
            return HobbyResponse(
                id=existing.id,
                user_id=existing.user_id,
                hobby=existing.hobby,
                created_at=existing.created_at,
            )

        obj = self.hobby_repo.create(obj_in={"user_id": user_id, "hobby": hobby})
        return HobbyResponse(id=obj.id, user_id=obj.user_id, hobby=obj.hobby, created_at=obj.created_at)

    def remove_hobby(self, user_id: UUID, hobby: str) -> bool:
        """
        Удаление хобби у пользователя

        Args:
            user_id: ID пользователя
            hobby: Название хобби

        Returns:
            bool: True если удалено успешно
        """
        return self.hobby_repo.delete_by_user_and_name(user_id=user_id, hobby=hobby)

    def add_coping_method(self, user_id: UUID, method: str) -> CopingMethodResponse:
        """
        Добавление метода совладания пользователю

        Args:
            user_id: ID пользователя
            method: Название метода

        Returns:
            CopingMethodResponse: Объект с данными метода
        """
        existing = self.coping_repo.get_by_user_and_name(user_id=user_id, method=method)
        if existing:
            return CopingMethodResponse(
                id=existing.id,
                user_id=existing.user_id,
                method=existing.method,
                created_at=existing.created_at,
            )

        obj = self.coping_repo.create(obj_in={"user_id": user_id, "method": method})
        return CopingMethodResponse(id=obj.id, user_id=obj.user_id, method=obj.method, created_at=obj.created_at)

    def remove_coping_method(self, user_id: UUID, method: str) -> bool:
        """
        Удаление метода совладания у пользователя

        Args:
            user_id: ID пользователя
            method: Название метода

        Returns:
            bool: True если удалено успешно
        """
        return self.coping_repo.delete_by_user_and_name(user_id=user_id, method=method)
