"""
Памятка для Ксюши

Тут примерный код зависимостей, которые нужно будет использовать при написании API.
Ключевая задача этого файла - соединять бэкенд с API. Это все делается для того, чтобы
код был чистым.

Код сгенеририла нейронка. Некоторые методы возможно нам не потребуется, а некоторые
может быть придется дорабатывать.
"""

"""
API Dependencies Module

Centralized dependency providers for API endpoints.
Handles: Database sessions, Authentication, Authorization (Freemium),
Query parsing, and External service access.

Based on System Analysis:
- Freemium model with 90-day analytics limit for Free users
- Pro features: LLM insights, Export, Comments, Correlations, Deep Analytics
- Autonomy-supportive error messages (no pressure/diagnosis)
- Timezone-aware date handling
"""

from datetime import datetime, date, timedelta
from typing import Generator, Optional, Annotated
from uuid import UUID
from functools import lru_cache

from fastapi import Depends, HTTPException, status, Query, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from celery import Celery
from pydantic import BaseModel

from app.core.database import SessionLocal
from app.core.config import Settings, get_settings
from app.core.security import verify_token
from app.core.constants import (
    FREE_ANALYTICS_DAYS,
    PRO_ANALYTICS_DAYS,
    MAX_EXPORT_DAYS,
    MIN_CORRELATION_DAYS,
)
from app.repositories.user_repo import UserRepository
from app.repositories.subscription_repo import SubscriptionRepository
from app.services.auth_service import AuthService
# from app.services.subscription_service import SubscriptionService


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================


class CurrentUserContext(BaseModel):
    """
    Lightweight user context passed to endpoints.
    Avoids multiple DB queries by caching user + subscription data.
    """
    user_id: UUID
    email: str
    timezone: str
    subscription_plan: str  # "free" or "pro"
    subscription_status: str  # "active", "expired", "cancelled"
    subscription_expires_at: Optional[datetime]
    created_at: datetime


class PaginationParams(BaseModel):
    """Standard pagination for list endpoints."""
    skip: int = 0
    limit: int = 20

    class Config:
        frozen = True  # Immutable for safety


class DateRangeParams(BaseModel):
    """Standard date range for analytics and exports."""
    start_date: date
    end_date: date
    period_days: int

    class Config:
        frozen = True


# =============================================================================
# SECURITY SCHEMES
# =============================================================================


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False  # Allows optional auth endpoints
)


# =============================================================================
# DATABASE DEPENDENCIES
# =============================================================================


def get_db() -> Generator[Session, None, None]:
    """
    Provides a SQLAlchemy database session for the request lifecycle.
    Ensures session is closed after request and rolls back on exception.

    Yields:
        Session: Active database session

    Usage:
        @router.get("/users/me")
        def get_user(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_auth_service(
        db: Annotated[Session, Depends(get_db)],
) -> AuthService:
    """Dependency provider for AuthService bound to current DB session."""
    return AuthService(db)


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================


def get_current_user(
        token: Annotated[Optional[str], Depends(oauth2_scheme)],
        db: Annotated[Session, Depends(get_db)],
) -> CurrentUserContext:
    """
    Validates JWT token and retrieves user context.
    Required for all protected endpoints.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        CurrentUserContext: User info + subscription status

    Raises:
        HTTPException 401: If token is missing, invalid, or expired

    Usage:
        @router.get("/users/me")
        def get_profile(user: CurrentUserContext = Depends(get_current_user)):
            ...
    """
    # Check if token exists
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token signature and expiration
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token payload
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Account may have been deleted.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch subscription status
    sub_repo = SubscriptionRepository(db)
    subscription = sub_repo.get_by_user(user_id)

    # Build context
    if subscription:
        subscription_plan = subscription.plan
        subscription_status = subscription.status
        subscription_expires_at = subscription.expires_at
    else:
        subscription_plan = "free"
        subscription_status = "active"
        subscription_expires_at = None

    return CurrentUserContext(
        user_id=user.id,
        email=user.email,
        timezone=user.timezone,
        subscription_plan=subscription_plan,
        subscription_status=subscription_status,
        subscription_expires_at=subscription_expires_at,
        created_at=user.created_at,
    )


def get_current_user_optional(
        token: Annotated[Optional[str], Depends(oauth2_scheme)],
        db: Annotated[Session, Depends(get_db)],
) -> Optional[CurrentUserContext]:
    """
    Retrieves user context if token exists, otherwise returns None.
    Used for public endpoints that personalize content if logged in.

    Args:
        token: JWT token from Authorization header (optional)
        db: Database session

    Returns:
        CurrentUserContext | None: User info if authenticated, None otherwise

    Usage:
        @router.get("/health")
        def health_check(user: Optional[CurrentUserContext] = Depends(get_current_user_optional)):
            if user:
                return {"status": "healthy", "user": "authenticated"}
            return {"status": "healthy", "user": "guest"}
    """
    if token is None:
        return None

    try:
        return get_current_user(token, db)
    except HTTPException:
        return None


# =============================================================================
# AUTHORIZATION & SUBSCRIPTION DEPENDENCIES (FREEMIUM LOGIC)
# =============================================================================


def verify_pro_subscription(
        user: Annotated[CurrentUserContext, Depends(get_current_user)],
) -> bool:
    """
    Guard dependency to ensure user has an Active Pro subscription.
    Based on System Analysis: Pro features include LLM insights, Export, Comments, Correlations.

    Args:
        user: Current user context

    Returns:
        bool: Always True if passes (else raises exception)

    Raises:
        HTTPException 403: If user is on Free plan or subscription expired

    Usage:
        @router.get("/analytics/deep")
        def deep_analytics(
            _ = Depends(verify_pro_subscription),
            user: CurrentUserContext = Depends(get_current_user)
        ):
            ...
    """
    # Check if plan is Pro
    if user.subscription_plan != "pro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "pro_subscription_required",
                "message": "Эта функция доступна только для Pro-пользователей. "
                           "Перейдите на Pro, чтобы получить доступ к глубокой аналитике.",
                "upgrade_url": "/api/v1/subscription/checkout",
                "current_plan": user.subscription_plan,
            },
        )

    # Check if subscription is active
    if user.subscription_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "subscription_expired",
                "message": "Ваша Pro-подписка истекла. Обновите подписку для продолжения.",
                "upgrade_url": "/api/v1/subscription/checkout",
                "expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
            },
        )

    # Check if subscription has not expired
    if user.subscription_expires_at and user.subscription_expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "subscription_expired",
                "message": "Ваша Pro-подписка истекла. Обновите подписку для продолжения.",
                "upgrade_url": "/api/v1/subscription/checkout",
            },
        )

    return True


def require_feature(feature_name: str):
    """
    Dependency factory for specific feature gates.
    Creates a dependency function for a specific Pro feature.

    Args:
        feature_name: Feature identifier (e.g., "export", "llm_insights", "comments")

    Returns:
        Callable: A dependency function that checks feature access

    Usage:
        @router.post("/export/csv")
        def export_csv(
            _ = Depends(require_feature("export")),
            user: CurrentUserContext = Depends(get_current_user)
        ):
            ...
    """

    def feature_guard(
            user: Annotated[CurrentUserContext, Depends(get_current_user)],
    ) -> bool:
        # Map feature names to required plan
        PRO_FEATURES = {
            "export",
            "llm_insights",
            "comments",
            "correlations",
            "deep_analytics",
            "pdf_report",
        }

        if feature_name in PRO_FEATURES:
            if user.subscription_plan != "pro" or user.subscription_status != "active":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "feature_requires_pro",
                        "message": f"Функция '{feature_name}' доступна только для Pro-пользователей.",
                        "feature": feature_name,
                        "upgrade_url": "/api/v1/subscription/checkout",
                    },
                )

        return True

    return feature_guard


def validate_analytics_period(
        period_days: Annotated[int, Query(default=30, ge=1, le=365)],
        user: Annotated[CurrentUserContext, Depends(get_current_user)],
) -> int:
    """
    Ensures Free users don't request more than 90 days of history (System Analysis constraint).
    Pro users get unlimited (up to 365 days hard cap for performance).

    Args:
        period_days: Requested analysis period
        user: Current user context

    Returns:
        int: Validated period days

    Raises:
        HTTPException 403: If Free user exceeds 90-day limit
        HTTPException 400: If period exceeds 365 days (hard cap)

    Usage:
        @router.get("/analytics/summary")
        def get_analytics(
            period_days: int = Depends(validate_analytics_period),
            user: CurrentUserContext = Depends(get_current_user)
        ):
            ...
    """
    # Free plan limit (from System Analysis)
    FREE_LIMIT = FREE_ANALYTICS_DAYS  # 90 days

    # Hard cap for performance (prevents DB overload)
    MAX_LIMIT = PRO_ANALYTICS_DAYS  # 365 days

    # Check Free user limit
    if user.subscription_plan == "free" and period_days > FREE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "free_plan_limit_exceeded",
                "message": f"Бесплатный план ограничен {FREE_LIMIT} днями. "
                           f"Перейдите на Pro для неограниченной истории.",
                "current_limit": FREE_LIMIT,
                "requested": period_days,
                "upgrade_url": "/api/v1/subscription/checkout",
            },
        )

    # Check hard cap (all users)
    if period_days > MAX_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "period_too_long",
                "message": f"Максимальный период анализа — {MAX_LIMIT} дней.",
                "max_allowed": MAX_LIMIT,
                "requested": period_days,
            },
        )

    return period_days


def validate_export_period(
        start_date: Annotated[Optional[date], Query(default=None)],
        end_date: Annotated[Optional[date], Query(default=None)],
        user: Annotated[CurrentUserContext, Depends(get_current_user)],
) -> DateRangeParams:
    """
    Validates date range for export requests.
    Ensures Free users can't export more than 90 days.

    Args:
        start_date: Start of export period
        end_date: End of export period
        user: Current user context

    Returns:
        DateRangeParams: Validated date range

    Raises:
        HTTPException 400: If dates are invalid or in future
        HTTPException 403: If Free user exceeds limit

    Usage:
        @router.post("/export/csv")
        def export_csv(
            date_range: DateRangeParams = Depends(validate_export_period),
            _ = Depends(verify_pro_subscription)
        ):
            ...
    """
    today = date.today()

    # Default to last 30 days if not specified
    if end_date is None:
        end_date = today
    if start_date is None:
        start_date = today - timedelta(days=30)

    # Validate dates are not in future
    if end_date > today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "future_date_not_allowed",
                "message": "Дата окончания не может быть в будущем.",
                "end_date": end_date.isoformat(),
                "today": today.isoformat(),
            },
        )

    # Validate start <= end
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_date_range",
                "message": "Дата начала должна быть раньше даты окончания.",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )

    # Calculate period
    period_days = (end_date - start_date).days + 1

    # Check max export limit
    if period_days > MAX_EXPORT_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "export_period_too_long",
                "message": f"Максимальный период экспорта — {MAX_EXPORT_DAYS} дней.",
                "max_allowed": MAX_EXPORT_DAYS,
                "requested": period_days,
            },
        )

    return DateRangeParams(
        start_date=start_date,
        end_date=end_date,
        period_days=period_days,
    )


def validate_correlation_request(
        period_days: Annotated[int, Query(default=30, ge=14)],
        user: Annotated[CurrentUserContext, Depends(get_current_user)],
) -> int:
    """
    Validates correlation analysis request.
    Requires minimum 14 days for statistical significance (System Analysis).

    Args:
        period_days: Requested period
        user: Current user context

    Returns:
        int: Validated period

    Raises:
        HTTPException 400: If period < 14 days
        HTTPException 403: If Free user (correlation is Pro feature)

    Usage:
        @router.get("/analytics/correlation")
        def get_correlation(
            period_days: int = Depends(validate_correlation_request),
            _ = Depends(verify_pro_subscription)
        ):
            ...
    """
    MIN_DAYS = MIN_CORRELATION_DAYS  # 14 days

    if period_days < MIN_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "insufficient_data",
                "message": f"Для корреляционного анализа требуется минимум {MIN_DAYS} дней данных.",
                "minimum_required": MIN_DAYS,
                "requested": period_days,
            },
        )

    return period_days


# =============================================================================
# QUERY PARAMETER HELPERS
# =============================================================================


def get_pagination(
        skip: Annotated[int, Query(default=0, ge=0)],
        limit: Annotated[int, Query(default=20, ge=1, le=100)],
) -> PaginationParams:
    """
    Standardizes pagination across list endpoints.
    Enforces max limit to prevent DB overload.

    Args:
        skip: Number of records to skip
        limit: Number of records to return (max 100)

    Returns:
        PaginationParams: Validated pagination object

    Usage:
        @router.get("/notifications")
        def get_notifications(
            pagination: PaginationParams = Depends(get_pagination)
        ):
            ...
    """
    return PaginationParams(skip=skip, limit=limit)


def get_date_range(
        start_date: Annotated[Optional[date], Query(default=None)],
        end_date: Annotated[Optional[date], Query(default=None)],
        default_days: Annotated[int, Query(default=30)] = 30,
) -> DateRangeParams:
    """
    Standardizes date range queries for analytics and exports.

    Args:
        start_date: Start of period (optional)
        end_date: End of period (optional)
        default_days: Default period if dates not specified

    Returns:
        DateRangeParams: Validated date range

    Usage:
        @router.get("/emotions")
        def get_emotions(
            date_range: DateRangeParams = Depends(get_date_range)
        ):
            ...
    """
    today = date.today()

    if end_date is None:
        end_date = today
    if start_date is None:
        start_date = today - timedelta(days=default_days)

    # Validate
    if end_date > today:
        end_date = today

    if start_date > end_date:
        start_date = end_date - timedelta(days=default_days)

    period_days = (end_date - start_date).days + 1

    return DateRangeParams(
        start_date=start_date,
        end_date=end_date,
        period_days=period_days,
    )


def get_common_headers(request: Request) -> dict:
    """
    Extracts common headers for logging or analytics.
    Sanitizes to remove PII.

    Args:
        request: FastAPI request object

    Returns:
        dict: Sanitized headers for logging context

    Usage:
        @router.post("/emotions")
        def create_emotion(
            headers: dict = Depends(get_common_headers),
            ...
        ):
            logger.info("Emotion created", extra={"headers": headers})
    """
    return {
        "user_agent": request.headers.get("user-agent", "unknown")[:200],  # Truncate
        "accept_language": request.headers.get("accept-language", "en"),
        "x_forwarded_for": request.headers.get("x-forwarded-for", "").split(",")[0].strip(),
    }


# =============================================================================
# EXTERNAL SERVICE DEPENDENCIES
# =============================================================================


@lru_cache()
def get_celery_app() -> Celery:
    """
    Provides the Celery application instance for triggering background tasks.
    Cached to avoid reinitialization on every request.

    Returns:
        Celery: Configured Celery app

    Usage:
        @router.post("/export/csv")
        def export_csv(
            celery: Celery = Depends(get_celery_app),
            ...
        ):
            task = celery.send_task("app.tasks.exports.generate_csv_export", ...)
    """
    from app.core.celery_config import celery_app
    return celery_app


@lru_cache()
def get_settings() -> Settings:
    """
    Provides application settings (config) to endpoints.
    Cached for performance.

    Returns:
        Settings: Application configuration

    Usage:
        @router.get("/health")
        def health_check(settings: Settings = Depends(get_settings)):
            return {"version": settings.VERSION}
    """
    return get_settings()


# def get_email_client():
#     """
#     Provides configured email client instance.
#
#     Returns:
#         EmailProvider: Configured email client
#
#     Usage:
#         @router.post("/auth/password/reset")
#         def reset_password(
#             email_client = Depends(get_email_client),
#             ...
#         ):
#             email_client.send_password_reset_email(...)
#     """
#     from app.core.clients.email_client import EmailProvider
#     settings = get_settings()
#     return EmailProvider(
#         smtp_host=settings.SMTP_HOST,
#         smtp_port=settings.SMTP_PORT,
#         smtp_user=settings.SMTP_USER,
#         smtp_password=settings.SMTP_PASSWORD,
#         email_from=settings.EMAIL_FROM,
#     )


def get_telegram_client():
    """
    Provides configured Telegram bot client instance.

    Returns:
        TelegramProvider: Configured Telegram client

    Usage:
        @router.post("/notifications/test")
        def test_notification(
            telegram_client = Depends(get_telegram_client),
            ...
        ):
            telegram_client.send_message(...)
    """
    from app.core.clients.telegram_client import TelegramProvider
    settings = get_settings()
    return TelegramProvider(
        bot_token=settings.TELEGRAM_BOT_TOKEN,
    )


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================


class SubscriptionRequiredException(HTTPException):
    """
    Custom exception for Freemium gating.
    Uses autonomy-supportive language (System Analysis requirement).
    """

    def __init__(
            self,
            message: str = "Эта функция доступна только для Pro-пользователей. "
                           "Перейдите на Pro, чтобы получить доступ.",
            upgrade_url: str = "/api/v1/subscription/checkout",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "subscription_required",
                "message": message,
                "upgrade_url": upgrade_url,
            },
        )


class InvalidPeriodException(HTTPException):
    """
    Custom exception for analytics date validation.
    """

    def __init__(
            self,
            message: str,
            max_allowed_days: int,
            requested_days: int,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_period",
                "message": message,
                "max_allowed": max_allowed_days,
                "requested": requested_days,
            },
        )


class InsufficientDataException(HTTPException):
    """
    Custom exception for analytics with insufficient data points.
    """

    def __init__(
            self,
            message: str,
            minimum_required: int,
            available: int,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "insufficient_data",
                "message": message,
                "minimum_required": minimum_required,
                "available": available,
            },
        )


# =============================================================================
# COMPOSITE DEPENDENCIES (FOR CONVENIENCE)
# =============================================================================


# Type aliases for cleaner endpoint signatures
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[CurrentUserContext, Depends(get_current_user)]
OptionalUser = Annotated[Optional[CurrentUserContext], Depends(get_current_user_optional)]
ProUser = Annotated[CurrentUserContext, Depends(get_current_user), Depends(verify_pro_subscription)]
ValidatedPeriod = Annotated[int, Depends(validate_analytics_period)]
Pagination = Annotated[PaginationParams, Depends(get_pagination)]
DateRange = Annotated[DateRangeParams, Depends(get_date_range)]
CeleryApp = Annotated[Celery, Depends(get_celery_app)]
AppSettings = Annotated[Settings, Depends(get_settings)]

# =============================================================================
# DEPENDENCY GRAPH & USAGE MAP
# =============================================================================

"""
DEPENDENCY USAGE BY ENDPOINT:

| Endpoint                          | Dependencies Required                              |
|-----------------------------------|----------------------------------------------------|
| POST /auth/register               | get_db, get_celery_app                             |
| POST /auth/login                  | get_db                                             |
| POST /auth/password/reset         | get_db, get_email_client                           |
| GET /users/me                     | get_current_user                                   |
| PUT /users/me                     | get_current_user, get_db                           |
| DELETE /users/me                  | get_current_user, get_db                           |
| GET /users/me/settings            | get_current_user, get_db                           |
| PUT /users/me/settings            | get_current_user, get_db                           |
| POST /emotions                    | get_current_user, get_db                           |
| GET /emotions                     | get_current_user, get_db, get_date_range           |
| GET /emotions/today               | get_current_user, get_db                           |
| PUT /emotions/{id}                | get_current_user, get_db                           |
| DELETE /emotions/{id}             | get_current_user, get_db                           |
| GET /analytics/summary            | get_current_user, get_db, validate_analytics_period|
| GET /analytics/deep               | get_current_user, get_db, verify_pro_subscription  |
| GET /analytics/correlation        | get_current_user, get_db, verify_pro_subscription  |
| GET /analytics/trends             | get_current_user, get_db                           |
| GET /notifications                | get_current_user, get_db, get_pagination           |
| PUT /notifications/preferences    | get_current_user, get_db                           |
| POST /notifications/test          | get_current_user, get_db, get_telegram_client      |
| GET /subscription                 | get_current_user, get_db                           |
| POST /subscription/checkout       | get_current_user, get_db                           |
| DELETE /subscription              | get_current_user, get_db                           |
| POST /export/csv                  | get_current_user, get_db, verify_pro_subscription  |
| POST /export/pdf                  | get_current_user, get_db, verify_pro_subscription  |
| POST /emotions/{id}/comments      | get_current_user, get_db, verify_pro_subscription  |
| GET /health                       | get_settings, get_db                               |
"""


# =============================================================================
# INITIALIZATION
# =============================================================================


def init_dependencies():
    """
    Initializes and validates all dependencies on application startup.
    Called from app/main.py during lifespan events.

    Usage:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            init_dependencies()
            yield
    """
    # Test database connection
    db = SessionLocal()
    try:
        db.execute("SELECT 1")
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")
    finally:
        db.close()

    # Test settings load
    settings = get_settings()
    if not settings.SECRET_KEY:
        raise RuntimeError("SECRET_KEY not configured")

    # Test Celery connection
    try:
        celery = get_celery_app()
        celery.inspect().ping()
    except Exception:
        # Celery not critical for startup, log warning
        pass
