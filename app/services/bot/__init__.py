"""
Telegram Bot module for daily reminders and user interaction.

This module provides a Telegram bot that:
- Handles user commands (/start, /help, /settings, /stop, /set_time)
- Sends daily reminders to users
- Integrates with the notification service for persistent storage
"""

from .handlers import MessageHandlers
from .bot_service import TelegramBotService

__all__ = ["TelegramBotService", "MessageHandlers"]
