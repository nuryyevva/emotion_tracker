"""
Telegram Client (Bot API)

Sends notifications via Telegram.
Based on System Analysis: Telegram is one of two notification channels.
"""

import requests
from typing import Optional
from app.core.config import settings


class TelegramProvider:
    """
    Telegram Bot API provider.
    """

    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or (
            settings.TELEGRAM_BOT_TOKEN.get_secret_value()
            if settings.TELEGRAM_BOT_TOKEN
            else None
        )
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.enabled = bool(self.bot_token)

    def send_message(
            self,
            chat_id: str,
            text: str,
            parse_mode: str = "HTML",
    ) -> bool:
        """
        Send message to Telegram chat.

        Args:
            chat_id: User's Telegram chat ID
            text: Message text (supports autonomy-supportive tone)
            parse_mode: Formatting mode (HTML/Markdown)

        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
            }

            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def send_trend_notification(
            self,
            chat_id: str,
            trend_type: str,
            message: str,
    ) -> bool:
        """
        Send trend-based notification.

        Args:
            chat_id: User's chat ID
            trend_type: Type of trend (e.g., "fatigue_high")
            message: Supportive message

        Returns:
            bool: Success status
        """
        # Add emoji based on trend
        emojis = {
            "fatigue_high": "😴",
            "anxiety_high": "😰",
            "mood_improvement": "🌟",
        }
        emoji = emojis.get(trend_type, "📊")

        text = f"{emoji} <b>Emotion Tracker</b>\n\n{message}"
        return self.send_message(chat_id, text)
