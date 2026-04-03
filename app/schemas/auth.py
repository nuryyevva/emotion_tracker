"""
Authentication schemas - registration, login, password reset.

Used in:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/password/reset
- POST /api/v1/auth/password/reset/confirm
- POST /api/v1/auth/refresh
"""

from pydantic import EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re

from .common import BaseSchema, UUIDMixin


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class UserRegister(BaseSchema):
    """
    User registration request.

    Used in: POST /api/v1/auth/register
    """
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters"
    )
    timezone: str = Field(
        default="UTC",
        description="IANA timezone (e.g., 'Europe/Moscow', 'Asia/Ashgabat')"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength.
        Requirements (from System Analysis):
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 digit
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseSchema):
    """
    User login request.

    Used in: POST /api/v1/auth/login
    """
    email: EmailStr
    password: str


class PasswordResetRequest(BaseSchema):
    """
    Password reset request.

    Used in: POST /api/v1/auth/password/reset
    """
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """
    Password reset confirmation.

    Used in: POST /api/v1/auth/password/reset/confirm
    """
    token: str
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Same validation as registration."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class TokenRefreshRequest(BaseSchema):
    """
    Token refresh request.

    Used in: POST /api/v1/auth/refresh
    """
    refresh_token: str


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class UserAuthResponse(UUIDMixin, BaseSchema):
    """User data in authentication response."""
    email: str
    created_at: datetime


class TokenResponse(BaseSchema):
    """
    JWT token response.

    Used in: POST /api/v1/auth/register, POST /api/v1/auth/login
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds
    user: Optional[UserAuthResponse] = None


class PasswordResetResponse(BaseSchema):
    """
    Password reset response.

    Used in: POST /api/v1/auth/password/reset, POST /api/v1/auth/password/reset/confirm
    """
    message: str


class TokenRefreshResponse(BaseSchema):
    """
    Token refresh response.

    Used in: POST /api/v1/auth/refresh
    """
    access_token: str
    expires_in: int = 1800
