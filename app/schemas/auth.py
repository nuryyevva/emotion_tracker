from pydantic import EmailStr, Field, field_validator
from .common import BaseSchema
import re

class UserRegister(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Минимум 8 символов")
    timezone: str = Field(default="UTC", description="Часовой пояс IANA (например, Europe/Moscow)")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v

class UserLogin(BaseSchema):
    email: EmailStr
    password: str

class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # секунд

class PasswordResetRequest(BaseSchema):
    email: EmailStr

class PasswordResetConfirm(BaseSchema):
    token: str
    new_password: str
