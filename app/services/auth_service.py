"""
Сервис аутентификации
"""
from datetime import timedelta

from sqlalchemy.orm import Session

from ..repositories.user_repo import UserRepository
from ..services.user_service import UserService
from ..schemas.auth import (TokenResponse, UserAuthResponse, UserRegister,
                            UserLogin, PasswordResetRequest, PasswordResetConfirm)
from ..schemas.common import UserStatus
from ..core.security import get_password_hash, verify_password, create_access_token


class AuthService:
    """Сервис для работы с аутентификацией"""

    def __init__(self, db: Session):
        """
        Инициализация сервиса аутентификации

        Args:
            db: Сессия базы данных
        """
        self.user_repo = UserRepository(db)
        self.user_service = UserService(db)

    def register(self, user_reg: UserRegister) -> TokenResponse:
        """
        Регистрация нового пользователя

        Args:
            user_reg: User registration request.

        Returns:
            TokenResponse: Объект с токенами
        """
        # Проверка существующего пользователя
        existing_user = self.user_repo.get_by_email(user_reg.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Создание пользователя
        password_hash = get_password_hash(user_reg.password)
        user = self.user_repo.create(
            obj_in = dict(
                email=user_reg.email,
                password_hash=password_hash,
                timezone=user_reg.timezone,
                status=UserStatus.ACTIVE
            )
        )

        # Создание настроек по умолчанию
        self.user_service.create_default_settings(user.id)

        # Генерация токенов
        access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(hours=1))
        refresh_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(hours=720))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user=UserAuthResponse(
                user_id=user.id,
                email=user_reg.email,
                created_at=user.created_at
            )
        )

    def login(self, user_login: UserLogin) -> TokenResponse:
        """
        Аутентификация пользователя

        Args:
            user_login: User login request.

        Returns:
            TokenResponse: Объект с токенами
        """
        user = self.user_repo.get_by_email(user_login.email)

        if not user or not verify_password(user_login.password, user.password_hash):
            raise ValueError("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            raise ValueError("Account is not active")

        access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(hours=1))
        refresh_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(hours=720))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user=UserAuthResponse(
                user_id=user.id,
                email=user.email,
                created_at=user.created_at
            )
        )

    def request_password_reset(self, pass_reset_req: PasswordResetRequest) -> bool:
        """
        Запрос на сброс пароля

        Args:
            pass_reset_req: Password reset request.

        Returns:
            bool: результат операции

        NOTE: Метод пока не реализован
        """
        raise NotImplementedError("request_password_reset method not implemented yet")

    def reset_password(self, pass_reset_req: PasswordResetConfirm) -> str:
        """
        Запрос на сброс пароля

        Args:
            pass_reset_req: Password reset request.

        Returns:
            bool: результат операции

        NOTE: Метод пока не реализован
        """
        raise NotImplementedError("reset_password method not implemented yet")