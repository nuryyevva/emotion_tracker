"""
Application Configuration

Loads environment variables and validates settings.
Based on System Analysis: Freemium model, external integrations (Email, Telegram, LLM, Payment).
"""

from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl, SecretStr


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =============================================================================
    # APPLICATION
    # =============================================================================
    PROJECT_NAME: str = Field(default="Emotion Tracker", description="Project name")
    VERSION: str = Field(default="1.0.0", description="API version")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API prefix")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # =============================================================================
    # DATABASE
    # =============================================================================
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string",
        examples=["postgresql://user:password@localhost:5432/emotion_tracker"]
    )
    DATABASE_POOL_SIZE: int = Field(default=5, description="DB connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="DB max overflow")

    # =============================================================================
    # SECURITY
    # =============================================================================
    SECRET_KEY: SecretStr = Field(
        ...,
        description="Secret key for JWT signing",
        min_length=32
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration in days"
    )
    BCRYPT_ROUNDS: int = Field(default=12, description="Password hashing rounds")

    # =============================================================================
    # CORS
    # =============================================================================
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=[],
        description="Allowed CORS origins"
    )
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS and redirects"
    )

    # =============================================================================
    # EMAIL (SMTP)
    # =============================================================================
    # SMTP_HOST: Optional[str] = Field(default=None, description="SMTP server host")
    # SMTP_PORT: int = Field(default=587, description="SMTP server port")
    # SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    # SMTP_PASSWORD: Optional[SecretStr] = Field(default=None, description="SMTP password")
    # EMAIL_FROM: str = Field(
    #     default="noreply@emotion-tracker.com",
    #     description="Sender email address"
    # )
    # EMAIL_ENABLED: bool = Field(default=False, description="Enable email notifications")

    # =============================================================================
    # TELEGRAM
    # =============================================================================
    TELEGRAM_BOT_TOKEN: Optional[SecretStr] = Field(
        default=None,
        description="Telegram Bot API token"
    )
    TELEGRAM_ENABLED: bool = Field(default=False, description="Enable Telegram notifications")

    # =============================================================================
    # LLM (AI Insights)
    # =============================================================================
    # LLM_API_KEY: Optional[SecretStr] = Field(
    #     default=None,
    #     description="LLM provider API key (e.g., OpenAI)"
    # )
    # LLM_MODEL: str = Field(default="gpt-3.5-turbo", description="LLM model name")
    # LLM_ENABLED: bool = Field(default=False, description="Enable LLM insights")

    # =============================================================================
    # PAYMENT
    # =============================================================================
    # PAYMENT_PROVIDER_KEY: Optional[SecretStr] = Field(
    #     default=None,
    #     description="Payment gateway API key (e.g., Stripe)"
    # )
    # PAYMENT_WEBHOOK_SECRET: Optional[SecretStr] = Field(
    #     default=None,
    #     description="Payment webhook signing secret"
    # )
    # PAYMENT_ENABLED: bool = Field(default=False, description="Enable payment processing")
    # PRO_PRICE_MONTHLY: int = Field(default=699, description="Pro plan monthly price in RUB")
    # PRO_PRICE_YEARLY: int = Field(default=6990, description="Pro plan yearly price in RUB")

    # =============================================================================
    # CELERY
    # =============================================================================
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL (Redis/RabbitMQ)"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend"
    )

    # =============================================================================
    # STORAGE (Exports)
    # =============================================================================
    # STORAGE_TYPE: str = Field(default="local", description="Storage type: local or s3")
    # STORAGE_PATH: str = Field(default="./exports", description="Local storage path")
    # STORAGE_BUCKET: Optional[str] = Field(default=None, description="S3 bucket name")
    # STORAGE_URL_EXPIRE_HOURS: int = Field(
    #     default=24,
    #     description="Export URL expiration in hours"
    # )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


settings = get_settings()
