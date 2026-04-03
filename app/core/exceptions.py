"""
Custom Exceptions

HTTP exceptions with autonomy-supportive error messages.
Based on API Specification error handling.
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class AppException(HTTPException):
    """
    Base class for all custom application exceptions.
    """

    def __init__(
            self,
            status_code: int,
            detail: Dict[str, Any],
            headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )


class SubscriptionRequiredException(AppException):
    """
    Raised when Free user tries to access Pro feature.
    Uses autonomy-supportive language (System Analysis).
    """

    def __init__(
            self,
            feature: str = "this feature",
            upgrade_url: str = "/api/v1/subscription/checkout",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "subscription_required",
                "message": f"{feature.capitalize()} доступна только для Pro-пользователей. "
                           f"Перейдите на Pro для доступа.",
                "upgrade_url": upgrade_url,
            },
        )


class InvalidPeriodException(AppException):
    """
    Raised when analytics period exceeds limits.
    """

    def __init__(
            self,
            max_allowed: int,
            requested: int,
            user_plan: str = "free",
    ):
        message = (
            f"Бесплатный план ограничен {max_allowed} днями. "
            f"Перейдите на Pro для неограниченной истории."
            if user_plan == "free"
            else f"Максимальный период анализа — {max_allowed} дней."
        )

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_period",
                "message": message,
                "max_allowed": max_allowed,
                "requested": requested,
            },
        )


class InsufficientDataException(AppException):
    """
    Raised when not enough data for analysis (e.g., correlation).
    """

    def __init__(
            self,
            minimum_required: int,
            available: int,
            analysis_type: str = "analysis",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "insufficient_data",
                "message": f"Для {analysis_type} требуется минимум {minimum_required} дней данных. "
                           f"У вас доступно {available} дней.",
                "minimum_required": minimum_required,
                "available": available,
            },
        )


class InvalidCredentialsException(AppException):
    """
    Raised when login fails.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_credentials",
                "message": "Неверный email или пароль.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


class ResourceNotFoundException(AppException):
    """
    Raised when requested resource not found.
    """

    def __init__(self, resource_type: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "not_found",
                "message": f"{resource_type} not found.",
            },
        )


class TrendDetectionException(AppException):
    """
    Raised when trend detection fails unexpectedly.
    """

    def __init__(self, message: str = "Failed to detect trends"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "trend_detection_failed",
                "message": message,
            },
        )
