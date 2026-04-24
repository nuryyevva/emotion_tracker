"""
Telegram Bot Service for daily reminders and user interaction.

This service integrates with the notification system to:
- Store user settings persistently in the database
- Send daily reminders via Telegram
- Handle user commands and update preferences
"""

import logging
from datetime import datetime, time
from typing import Optional, Dict, Any
import threading
import time as time_module
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.bot.handlers import MessageHandlers
from app.repositories.user_settings_repo import UserSettingsRepository
from app.repositories.user_repo import UserRepository
from app.schemas.common import NotificationChannel

logger = logging.getLogger(__name__)


class TelegramBotService:
    """
    Telegram bot service for daily reminders.
    
    This service handles:
    - User command processing (/start, /help, /settings, /stop, /set_time)
    - Daily reminder scheduling and sending
    - Integration with notification service for persistent storage
    """

    def __init__(
        self,
        db: Session,
        bot_token: str,
        frontend_url: str = "http://localhost:3000",
    ):
        """
        Initialize the Telegram bot service.

        Args:
            db: Database session for persistent storage
            bot_token: Telegram bot token
            frontend_url: Base URL for the frontend web app (for survey links)
        """
        self.db = db
        self.bot_token = bot_token
        self.frontend_url = frontend_url.rstrip('/')
        self.handlers = MessageHandlers()
        self.settings_repo = UserSettingsRepository(db)
        self.user_repo = UserRepository(db)
        self._reminder_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_update_id = 0

    def _send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message via Telegram API.

        Args:
            chat_id: Target chat ID
            text: Message text
            parse_mode: Formatting mode (Markdown/HTML)

        Returns:
            bool: True if message was sent successfully
        """
        import requests

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False

    def _get_updates(self, offset: Optional[int] = None) -> list:
        """
        Get updates from Telegram API.

        Args:
            offset: Offset for polling

        Returns:
            list: List of updates
        """
        import requests

        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset

        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                return data.get("result", [])
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")

        return []

    def _get_user_by_chat_id(self, chat_id: str) -> Optional[Any]:
        """
        Find a user by their Telegram chat ID.

        Args:
            chat_id: Telegram chat ID

        Returns:
            User object or None if not found
        """
        from sqlalchemy import select
        from app.models import User
        
        stmt = select(User).where(User.telegram_chat_id == chat_id)
        result = self.db.scalars(stmt).first()
        return result

    def _process_message(self, message: dict) -> None:
        """
        Process an incoming Telegram message.

        Args:
            message: Telegram message object
        """
        chat_id = str(message.get("chat", {}).get("id"))
        text = message.get("text", "").strip()

        if not chat_id or not text:
            return

        logger.info(f"Received message from {chat_id}: {text}")

        # Get user by chat_id
        user = self._get_user_by_chat_id(chat_id)
        user_id = user.id if user else None

        # Process commands
        if text == "/start":
            response = self.handlers.start_handler()
            # Register/update user's Telegram chat ID
            if user and user_id:
                # Ensure user has notification settings
                settings = self.settings_repo.get_by_user(user_id)
                if not settings:
                    self.settings_repo.create_default(user_id=user_id)
                else:
                    # Enable reminders when user starts the bot
                    self.settings_repo.update(
                        settings=settings,
                        enabled=True,
                        channel=NotificationChannel.TELEGRAM,
                    )

        elif text == "/help":
            response = self.handlers.help_handler()

        elif text == "/settings":
            if user and user_id:
                settings = self.settings_repo.get_by_user(user_id)
                reminder_time = "20:00"
                if settings:
                    reminder_time = settings.notify_window_start.strftime("%H:%M")
                response = self.handlers.settings_handler(reminder_time)
            else:
                response = "❌ Пожалуйста, сначала используйте /start для регистрации."

        elif text == "/stop":
            if user and user_id:
                settings = self.settings_repo.get_by_user(user_id)
                if settings:
                    self.settings_repo.update(settings=settings, enabled=False)
            response = self.handlers.stop_handler()

        elif text.startswith("/set_time"):
            parts = text.split()
            if len(parts) == 2:
                time_str = parts[1]
                response = self.handlers.set_time_handler(time_str)
                if "✅" in response and user and user_id:
                    # Parse time and update settings
                    try:
                        hour, minute = map(int, time_str.split(':'))
                        new_time = time(hour, minute)
                        settings = self.settings_repo.get_by_user(user_id)
                        if settings:
                            self.settings_repo.update(
                                settings=settings,
                                window_start=new_time,
                                # Adjust window_end to be 2 hours after start
                                window_end=time((hour + 2) % 24, minute),
                                enabled=True,
                            )
                    except ValueError:
                        response = "❌ Неверный формат времени. Используйте HH:MM (например, 21:30)"
            else:
                response = "❌ Используйте: /set_time HH:MM"

        else:
            response = self.handlers.unknown_handler()

        self._send_message(chat_id, response)

    def send_reminder(self, chat_id: str) -> bool:
        """
        Send a daily reminder to a user.

        Args:
            chat_id: Telegram chat ID

        Returns:
            bool: True if reminder was sent successfully
        """
        survey_url = f"{self.frontend_url}/survey?tg_chat_id={chat_id}"
        message = self.handlers.reminder_message(survey_url)
        return self._send_message(chat_id, message)

    def _check_and_send_reminders(self) -> None:
        """Check and send reminders to all users based on their settings."""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # Get all users with Telegram notifications enabled
        from sqlalchemy import select
        from app.models import User, UserSettings
        
        stmt = (
            select(User, UserSettings)
            .join(UserSettings, User.id == UserSettings.user_id)
            .where(
                User.telegram_chat_id.isnot(None),
                UserSettings.reminders_enabled == True,
                UserSettings.notify_channel.in_([NotificationChannel.TELEGRAM, NotificationChannel.BOTH]),
            )
        )
        
        results = self.db.execute(stmt).all()
        
        for user, settings in results:
            reminder_time = settings.notify_window_start.strftime("%H:%M")
            
            if current_time == reminder_time:
                # Check if already sent today
                last_sent = getattr(settings, '_last_reminder_date', None)
                today = now.date().isoformat()

                if last_sent != today:
                    self.send_reminder(user.telegram_chat_id)
                    # Note: In production, you'd want to persist this in the database
                    setattr(settings, '_last_reminder_date', today)
                    logger.info(f"Sent reminder to user {user.id} ({user.telegram_chat_id})")

    def _polling_loop(self) -> None:
        """Main polling loop for receiving messages."""
        while self._running:
            try:
                # Get new messages
                updates = self._get_updates(
                    offset=self._last_update_id + 1 if self._last_update_id else None
                )

                for update in updates:
                    self._last_update_id = update.get("update_id", self._last_update_id)
                    message = update.get("message")

                    if message:
                        self._process_message(message)

                # Check and send reminders
                self._check_and_send_reminders()

                # Pause between requests
                time_module.sleep(1)

            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time_module.sleep(5)

    def start(self) -> None:
        """Start the Telegram bot in a background thread."""
        if self._running:
            logger.warning("Bot is already running")
            return

        self._running = True
        logger.info("Starting Telegram bot...")

        # Start in a separate thread
        self._reminder_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self._reminder_thread.start()

        logger.info("Telegram bot started successfully")

    def stop(self) -> None:
        """Stop the Telegram bot."""
        self._running = False
        logger.info("Telegram bot stopped")

    def register_user(self, user_id: UUID, chat_id: str) -> bool:
        """
        Register a user's Telegram chat ID.

        Args:
            user_id: User's UUID
            chat_id: Telegram chat ID

        Returns:
            bool: True if registration was successful
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False

        # Update user's Telegram chat ID
        from sqlalchemy import update
        from app.models import User
        
        stmt = update(User).where(User.id == user_id).values(telegram_chat_id=chat_id)
        self.db.execute(stmt)
        self.db.commit()

        # Create or update user settings for Telegram notifications
        settings = self.settings_repo.get_by_user(user_id)
        if not settings:
            self.settings_repo.create_default(user_id=user_id)
            # Update to use Telegram
            settings = self.settings_repo.get_by_user(user_id)
        
        if settings:
            self.settings_repo.update(
                settings=settings,
                channel=NotificationChannel.TELEGRAM,
                enabled=True,
            )

        return True

    def unregister_user(self, user_id: UUID) -> bool:
        """
        Unregister a user's Telegram chat ID.

        Args:
            user_id: User's UUID

        Returns:
            bool: True if unregistration was successful
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False

        # Clear user's Telegram chat ID
        from sqlalchemy import update
        from app.models import User
        
        stmt = update(User).where(User.id == user_id).values(telegram_chat_id=None)
        self.db.execute(stmt)
        self.db.commit()

        # Disable Telegram notifications
        settings = self.settings_repo.get_by_user(user_id)
        if settings:
            self.settings_repo.update(
                settings=settings,
                enabled=False,
            )

        return True
