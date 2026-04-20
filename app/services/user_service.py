"""
Сервис пользователей
"""
from datetime import time
from uuid import UUID
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from ..repositories.user_repo import UserRepository
from ..repositories.user_settings_repo import UserSettingsRepository
from ..repositories.hobby_repo import UserHobbyRepository
from ..repositories.coping_method_repo import UserCopingMethodRepository
from ..schemas.user import (
    UserResponse,
    UserSettingsResponse,
    HobbyResponse,
    CopingMethodResponse,
)
from ..models import NotifyChannel, NotifyFrequency


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db: Session):
        """
        Инициализация сервиса пользователей

        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.user_repo = UserRepository()
        self.settings_repo = UserSettingsRepository()
        self.hobby_repo = UserHobbyRepository()
        self.coping_repo = UserCopingMethodRepository()

    def get_profile(self, user_id: UUID) -> UserResponse:
        """
        Получение профиля пользователя

        Args:
            user_id: ID пользователя

        Returns:
            UserResponse: Объект с данными профиля
        """
        user = self.user_repo.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")

        return UserResponse(
            id=user.id,
            email=user.email,
            timezone=user.timezone,
            status=user.status.value if hasattr(user.status, 'value') else str(user.status),
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    def create_default_settings(self, user_id: UUID) -> None:
        """
        Создание настроек по умолчанию для нового пользователя

        Args:
            user_id: ID пользователя
        """
        self.settings_repo.create_default(self.db, user_id=user_id)

    def get_settings(self, user_id: UUID) -> UserSettingsResponse:
        """
        Получение настроек пользователя

        Args:
            user_id: ID пользователя

        Returns:
            UserSettingsResponse: Объект с настройками
        """
        settings = self.settings_repo.get_by_user(self.db, user_id)
        if not settings:
            settings = self.settings_repo.create_default(self.db, user_id=user_id)

        hobbies = self.hobby_repo.list_by_user(self.db, user_id)
        coping_methods = self.coping_repo.list_by_user(self.db, user_id)

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
            updated_at=settings.updated_at or settings.created_at,
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
        settings = self.settings_repo.get_by_user(self.db, user_id)
        if not settings:
            settings = self.settings_repo.create_default(self.db, user_id=user_id)

        # Обновление полей
        update_data = {}

        if "weekday_wake_up" in update:
            update_data["weekday_wake_up"] = update["weekday_wake_up"]
        if "weekday_bedtime" in update:
            update_data["weekday_bedtime"] = update["weekday_bedtime"]
        if "weekend_wake_up" in update:
            update_data["weekend_wake_up"] = update["weekend_wake_up"]
        if "weekend_bedtime" in update:
            update_data["weekend_bedtime"] = update["weekend_bedtime"]
        if "notify_channel" in update:
            update_data["notify_channel"] = update["notify_channel"]
        if "notify_window_start" in update:
            update_data["notify_window_start"] = update["notify_window_start"]
        if "notify_window_end" in update:
            update_data["notify_window_end"] = update["notify_window_end"]
        if "notify_frequency" in update:
            update_data["notify_frequency"] = update["notify_frequency"]
        if "reminders_enabled" in update:
            update_data["reminders_enabled"] = update["reminders_enabled"]

        if update_data:
            self.settings_repo.update(self.db, settings=settings, **update_data)

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
        user_hobby = self.hobby_repo.add(self.db, user_id=user_id, hobby=hobby)

        return HobbyResponse(
            id=user_hobby.id,
            user_id=user_id,
            hobby=user_hobby.hobby,
            created_at=user_hobby.created_at
        )

    def remove_hobby(self, user_id: UUID, hobby: str) -> bool:
        """
        Удаление хобби у пользователя

        Args:
            user_id: ID пользователя
            hobby: Название хобби

        Returns:
            bool: True если удалено успешно
        """
        return self.hobby_repo.remove(self.db, user_id=user_id, hobby=hobby)

    def add_coping_method(self, user_id: UUID, method: str) -> CopingMethodResponse:
        """
        Добавление метода совладания пользователю

        Args:
            user_id: ID пользователя
            method: Название метода

        Returns:
            CopingMethodResponse: Объект с данными метода
        """
        coping_method = self.coping_repo.add(self.db, user_id=user_id, method=method)

        return CopingMethodResponse(
            id=coping_method.id,
            user_id=user_id,
            method=coping_method.method,
            created_at=coping_method.created_at
        )

    def remove_coping_method(self, user_id: UUID, method: str) -> bool:
        """
        Удаление метода совладания у пользователя

        Args:
            user_id: ID пользователя
            method: Название метода

        Returns:
            bool: True если удалено успешно
        """
        return self.coping_repo.remove(self.db, user_id=user_id, method=method)