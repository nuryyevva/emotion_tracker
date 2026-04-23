"""
Telegram bot for daily reminders
"""
import logging
from datetime import datetime, time
from typing import Optional, Dict, Any
import threading
import time as time_module

from app.bot.handlers import MessageHandlers

# Настройка логирования
logger = logging.getLogger(__name__)


class TelegramBot:
    """Простой Telegram бот для напоминаний (без внешних библиотек)"""

    def __init__(self, bot_token: str, web_app_url: str = "https://emotions-tracker.com/survey"):
        """
        Инициализация бота

        Args:
            bot_token: Токен Telegram бота
            web_app_url: URL для опроса
        """
        self.bot_token = bot_token
        self.web_app_url = web_app_url
        self.handlers = MessageHandlers()
        self._user_settings: Dict[str, Dict[str, Any]] = {}  # {chat_id: {"reminder_time": "20:00", "enabled": True}}
        self._reminder_thread = None
        self._running = False

    def _send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Отправка сообщения через Telegram API

        Args:
            chat_id: ID чата
            text: Текст сообщения
            parse_mode: Режим форматирования

        Returns:
            bool: True если отправлено успешно
        """
        import requests

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False

    def _get_updates(self, offset: Optional[int] = None) -> list:
        """
        Получение обновлений от Telegram API

        Args:
            offset: Смещение для получения следующих обновлений

        Returns:
            list: Список обновлений
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

    def _process_message(self, message: dict) -> None:
        """
        Обработка входящего сообщения

        Args:
            message: Сообщение от Telegram
        """
        chat_id = str(message.get("chat", {}).get("id"))
        text = message.get("text", "").strip()

        if not chat_id or not text:
            return

        logger.info(f"Received message from {chat_id}: {text}")

        # Обработка команд
        if text == "/start":
            response = self.handlers.start_handler()
            self._user_settings[chat_id] = {"reminder_time": "20:00", "enabled": True}

        elif text == "/help":
            response = self.handlers.help_handler()

        elif text == "/settings":
            settings = self._user_settings.get(chat_id, {"reminder_time": "20:00", "enabled": True})
            response = self.handlers.settings_handler(settings.get("reminder_time", "20:00"))

        elif text == "/stop":
            if chat_id in self._user_settings:
                self._user_settings[chat_id]["enabled"] = False
            response = self.handlers.stop_handler()

        elif text.startswith("/set_time"):
            parts = text.split()
            if len(parts) == 2:
                time_str = parts[1]
                response = self.handlers.set_time_handler(time_str)
                if "✅" in response:
                    if chat_id not in self._user_settings:
                        self._user_settings[chat_id] = {"reminder_time": "20:00", "enabled": True}
                    self._user_settings[chat_id]["reminder_time"] = time_str
            else:
                response = "❌ Используйте: /set_time HH:MM"

        else:
            response = self.handlers.unknown_handler()

        self._send_message(chat_id, response)

    def send_reminder(self, chat_id: str) -> bool:
        """
        Отправка напоминания пользователю

        Args:
            chat_id: ID чата

        Returns:
            bool: True если отправлено успешно
        """
        survey_url = f"{self.web_app_url}?tg_chat_id={chat_id}"
        message = self.handlers.reminder_message(survey_url)
        return self._send_message(chat_id, message)

    def _check_and_send_reminders(self) -> None:
        """Проверка и отправка напоминаний всем пользователям"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        for chat_id, settings in self._user_settings.items():
            if not settings.get("enabled", True):
                continue

            reminder_time = settings.get("reminder_time", "20:00")

            if current_time == reminder_time:
                # Проверяем, не отправляли ли уже сегодня
                last_sent = settings.get("last_sent_date")
                today = now.date().isoformat()

                if last_sent != today:
                    self.send_reminder(chat_id)
                    settings["last_sent_date"] = today

    def _polling_loop(self) -> None:
        """Основной цикл получения сообщений"""
        last_update_id = 0

        while self._running:
            try:
                # Получаем новые сообщения
                updates = self._get_updates(offset=last_update_id + 1 if last_update_id else None)

                for update in updates:
                    last_update_id = update.get("update_id", last_update_id)
                    message = update.get("message")

                    if message:
                        self._process_message(message)

                # Проверяем напоминания
                self._check_and_send_reminders()

                # Пауза между запросами
                time_module.sleep(1)

            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time_module.sleep(5)

    def start(self) -> None:
        """Запуск бота"""
        if self._running:
            logger.warning("Bot is already running")
            return

        self._running = True
        logger.info("Starting Telegram bot...")

        # Запускаем в отдельном потоке
        self._reminder_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self._reminder_thread.start()

        logger.info("Telegram bot started successfully")

    def stop(self) -> None:
        """Остановка бота"""
        self._running = False
        logger.info("Telegram bot stopped")

    def get_user_settings(self, chat_id: str) -> Dict[str, Any]:
        """Получение настроек пользователя"""
        return self._user_settings.get(chat_id, {"reminder_time": "20:00", "enabled": True})

    def set_user_settings(self, chat_id: str, settings: Dict[str, Any]) -> None:
        """Установка настроек пользователя"""
        if chat_id not in self._user_settings:
            self._user_settings[chat_id] = {}
        self._user_settings[chat_id].update(settings)