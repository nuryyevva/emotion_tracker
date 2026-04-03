"""
External Service Clients

Abstracted clients for Email, Telegram, LLM, and Payment.
Keeps Services clean from provider-specific logic.
"""

from .telegram_client import TelegramProvider

__all__ = [
    "TelegramProvider",
]
