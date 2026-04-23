@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)) -> TokenResponse:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        timezone=payload.timezone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        {"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(
        {"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token, user=user)


"""
Сервис аутентификации
"""
from datetime import timedelta
import jwt


from sqlalchemy.orm import Session

from ..repositories.user_repo import UserRepository
from ..services.user_service import UserService
from ..schemas.auth import (TokenResponse, UserAuthResponse, UserRegister,
                            UserLogin, PasswordResetRequest, PasswordResetConfirm)
from ..models import UserStatus
from ..core import settings
from ..core.security import get_password_hash, verify_password, create_access_token, verify_token


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
            email=user_reg.email,
            password_hash=password_hash,
            timezone=user_reg.timezone,
            status=UserStatus.ACTIVE
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
        user = self.user_repo.get_by_email(self.db, user_login.email)

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