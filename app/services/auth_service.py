"""
Сервис аутентификации.
"""
from datetime import timedelta
from secrets import token_urlsafe
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService
from app.schemas.auth import (
    TokenRefreshResponse,
    TokenResponse,
    UserAuthResponse,
    UserRegister,
    UserLogin,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.schemas.common import UserStatus
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.config import settings


class AuthService:
    """Сервис для работы с аутентификацией"""

    def __init__(self, db: Session):
        """
        Инициализация сервиса аутентификации

        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.user_repo = UserRepository()
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
        existing_user = self.user_repo.get_by_email(self.db, user_reg.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Создание пользователя
        password_hash = get_password_hash(user_reg.password)
        user = self.user_repo.create(
            self.db,
            obj_in=dict(
                email=user_reg.email,
                password_hash=password_hash,
                timezone=user_reg.timezone,
                status=UserStatus.ACTIVE
            )
        )

        # Создание настроек по умолчанию
        self.user_service.create_default_settings(user.id)

        # Генерация токенов
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(str(user.id))
        self.db.commit()

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
        user = self.user_repo.get_by_email(self.db, user_login.email)

        if not user or not verify_password(user_login.password, user.password_hash):
            raise ValueError("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            raise ValueError("Account is not active")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(str(user.id))

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

    def refresh_token(self, refresh_token: str) -> TokenRefreshResponse:
        """
        Обновление access/refresh токенов по refresh токену.

        Args:
            refresh_token: JWT refresh token.

        Returns:
            TokenRefreshResponse: Обновленная пара токенов.
        """
        payload = verify_token(refresh_token)
        if payload is None:
            raise ValueError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid refresh token payload")

        try:
            user_uuid = UUID(str(user_id))
        except ValueError as exc:
            raise ValueError("Invalid refresh token payload") from exc

        user = self.user_repo.get(self.db, user_uuid)
        if user is None:
            raise ValueError("User not found")
        if user.status != UserStatus.ACTIVE:
            raise ValueError("Account is not active")

        access_token = create_access_token(data={"sub": str(user_id)})
        new_refresh_token = create_refresh_token(str(user_id))
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return TokenRefreshResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    def request_password_reset(self, pass_reset_req: PasswordResetRequest) -> str:
        """
        Запрос на сброс пароля.

        Args:
            pass_reset_req: Password reset request.

        Returns:
            str: Временный reset token.
        """
        user = self.user_repo.get_by_email(self.db, pass_reset_req.email)
        if user is None:
            # Не раскрываем существование email.
            return ""

        reset_token = create_access_token(
            data={
                "sub": str(user.id),
                "type": "password_reset",
                "nonce": token_urlsafe(8),
            },
            expires_delta=timedelta(minutes=30),
        )
        return reset_token

    def reset_password(self, pass_reset_req: PasswordResetConfirm) -> str:
        """
        Запрос на сброс пароля

        Args:
            pass_reset_req: Password reset request.

        Returns:
            bool: результат операции

        """
        payload = verify_token(pass_reset_req.token)
        if payload is None:
            raise ValueError("Invalid or expired reset token")

        if payload.get("type") != "password_reset":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid reset token payload")

        try:
            user_uuid = UUID(str(user_id))
        except ValueError as exc:
            raise ValueError("Invalid reset token payload") from exc

        user = self.user_repo.get(self.db, user_uuid)
        if user is None:
            raise ValueError("User not found")
        if user.status != UserStatus.ACTIVE:
            raise ValueError("Account is not active")

        user.password_hash = get_password_hash(pass_reset_req.new_password)
        self.db.flush()
        self.db.commit()
        return "Password reset successfully"