"""
Сервис аутентификации
"""
from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, Any, Optional
import jwt
import hashlib
import secrets

from sqlalchemy.orm import Session

from ..repositories.user_repo import UserRepository
from ..services.user_service import UserService
from ..schemas.auth import TokenResponse, UserAuthResponse
from ..models import UserStatus


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
        self.secret_key = "your-secret-key-change-in-production"

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{hash_obj.hex()}:{salt}"

    def _verify_password(self, plain: str, hashed: str) -> bool:
        """Проверка пароля"""
        try:
            stored_hash, salt = hashed.split(":")
            new_hash = hashlib.pbkdf2_hmac('sha256', plain.encode(), salt.encode(), 100000).hex()
            return new_hash == stored_hash
        except:
            return False

    def _generate_token(self, user_id: UUID, expires_in_hours: int = 24) -> str:
        """Генерация JWT токена"""
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def register(self, email: str, password: str, timezone: str) -> TokenResponse:
        """
        Регистрация нового пользователя

        Args:
            email: Email пользователя
            password: Пароль
            timezone: Временная зона

        Returns:
            TokenResponse: Объект с токенами
        """
        # Проверка существующего пользователя
        existing_user = self.user_repo.get_by_email(self.db, email)
        if existing_user:
            raise ValueError("Email already registered")

        # Создание пользователя
        password_hash = self._hash_password(password)
        user = self.user_repo.create(
            self.db,
            email=email,
            password_hash=password_hash,
            timezone=timezone,
            status=UserStatus.ACTIVE
        )

        # Создание настроек по умолчанию
        self.user_service.create_default_settings(user.id)

        # Генерация токенов
        access_token = self._generate_token(user.id, expires_in_hours=1)
        refresh_token = self._generate_token(user.id, expires_in_hours=720)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,
            user=UserAuthResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at
            )
        )

    def login(self, email: str, password: str) -> TokenResponse:
        """
        Аутентификация пользователя

        Args:
            email: Email пользователя
            password: Пароль

        Returns:
            TokenResponse: Объект с токенами
        """
        user = self.user_repo.get_by_email(self.db, email)

        if not user or not self._verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            raise ValueError("Account is not active")

        access_token = self._generate_token(user.id, expires_in_hours=1)
        refresh_token = self._generate_token(user.id, expires_in_hours=720)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user=UserAuthResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at
            )
        )

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Проверка валидности токена

        Args:
            token: JWT токен

        Returns:
            dict: Данные из токена
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return {"valid": True, "user_id": payload.get("sub"), "payload": payload}
        except jwt.InvalidTokenError as e:
            return {"valid": False, "error": str(e)}

    def request_password_reset(self, email: str) -> bool:
        """
        Запрос на сброс пароля

        Args:
            email: Email пользователя

        Returns:
            bool: результат операции

        NOTE: Метод пока не реализован
        """
        raise NotImplementedError("request_password_reset method not implemented yet")