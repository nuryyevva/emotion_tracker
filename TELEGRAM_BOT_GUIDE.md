# Telegram Bot & Notification System - Complete Guide

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [How Telegram Chat ID is Added](#how-telegram-chat-id-is-added)
3. [Complete User Flow](#complete-user-flow)
4. [How Notifications Are Sent](#how-notifications-are-sent)
5. [Notification Preferences](#notification-preferences)
6. [Module Communication](#module-communication)
7. [File Structure](#file-structure)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEB APPLICATION                          │
│  (FastAPI - /api/v1/users, /api/v1/notifications)              │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ UserService  │  │Notification  │  │ BotService   │           │
│  │              │  │  Service     │  │ (Telegram)   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REPOSITORY LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ UserRepo     │  │Notification  │  │UserSettings  │           │
│  │              │  │  Repo        │  │  Repo        │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ users        │  │notification_ │  │user_settings │           │
│  │ (with        │  │  logs        │  │              │           │
│  │ telegram_    │  │              │  │              │           │
│  │ chat_id)     │  │              │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                        ▲
                        │
┌───────────────────────┴─────────────────────────────────────────┐
│                    TELEGRAM BOT                                 │
│  (Background thread in TelegramBotService)                      │
│  - Polls for messages every 1 second                            │
│  - Sends daily reminders at configured times                    │
│  - Handles commands: /start, /help, /settings, /stop            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 How Telegram Chat ID is Added

### **The Problem You Identified:**

> "How can our bot find the user by tg chat id, if he on our web app never added anything?"

You're absolutely right! The old implementation had a logical flaw. Here's the **corrected flow**:

### **Solution: Deep Linking from Web App to Bot**

#### **Step 1: User Registers on Web App**
```
User → Web App → POST /api/v1/auth/register
→ User created in database with:
   - id: uuid-12345
   - email: user@example.com
   - telegram_chat_id: NULL (not linked yet)
```

#### **Step 2: User Goes to Settings Page**
```
User clicks "Connect Telegram" button on web app
→ Web app generates deep link:
   https://t.me/YourBotName?start=uuid-12345
```

#### **Step 3: User Clicks Deep Link**
```
User clicks link → Opens Telegram → Starts bot
→ Telegram sends message to bot: "/start uuid-12345"
```

#### **Step 4: Bot Processes Deep Link**
```python
# In bot_service.py - _handle_deep_link()
1. Extract UUID from payload: "uuid-12345"
2. Find user in database by UUID
3. Link chat_id to user:
   UPDATE users SET telegram_chat_id = '987654321' 
   WHERE id = 'uuid-12345'
4. Enable Telegram notifications in user_settings
5. Send confirmation message to user
```

#### **Step 5: User Receives Confirmation**
```
Bot sends: "✅ Аккаунт успешно привязан!
            Здравствуйте, user@example.com!
            Теперь вы будете получать уведомления..."
```

---

## 🔄 Complete User Flow

### **Scenario A: New User Registration**

```
1. User visits web app
   ↓
2. User registers: POST /api/v1/auth/register
   ↓
3. AuthService creates user in database
   - users table: id, email, password_hash, telegram_chat_id=NULL
   ↓
4. UserService creates default settings
   - user_settings table: notify_channel=EMAIL, reminders_enabled=TRUE
   ↓
5. User receives JWT tokens
   ↓
6. User is logged in
```

### **Scenario B: Connecting Telegram Account**

```
1. Logged-in user goes to Settings page
   ↓
2. User clicks "Connect Telegram" button
   ↓
3. Web app generates deep link:
   https://t.me/YourBotName?start={user_id}
   ↓
4. User clicks link → Opens Telegram
   ↓
5. User presses "Start" in Telegram
   ↓
6. Bot receives: "/start {user_id}"
   ↓
7. Bot validates user_id exists in database
   ↓
8. Bot links chat_id to user:
   - Updates users.telegram_chat_id
   - Updates user_settings.notify_channel = TELEGRAM
   ↓
9. Bot sends confirmation message
   ↓
10. User now receives Telegram notifications!
```

### **Scenario C: Regular /start Command (No Deep Link)**

```
1. User finds bot in Telegram search
   ↓
2. User presses "Start"
   ↓
3. Bot receives: "/start" (no payload)
   ↓
4. Bot checks if chat_id is already linked to a user
   ↓
5a. If linked: Enable reminders, send welcome message
5b. If NOT linked: Send message explaining they need to 
    connect via web app first
```

---

## 📬 How Notifications Are Sent

### **Type 1: Daily Reminders (Automatic)**

```python
# Background thread in TelegramBotService
while bot_is_running:
    current_time = datetime.now().strftime("%H:%M")
    
    # Query database for users who should receive reminder NOW
    users = db.query(User, UserSettings).join(
        UserSettings, User.id == UserSettings.user_id
    ).filter(
        User.telegram_chat_id != NULL,
        UserSettings.reminders_enabled == TRUE,
        UserSettings.notify_channel IN [TELEGRAM, BOTH],
        TIME(UserSettings.notify_window_start) == current_time
    )
    
    for user, settings in users:
        # Check if already sent today
        if not sent_today(user.id):
            send_reminder(user.telegram_chat_id)
            mark_as_sent(user.id, today)
```

**Message Example:**
```
🌅 Ежедневное напоминание

Как вы себя чувствуете сегодня?
Пожалуйста, уделите 2 минуты, чтобы отметить свои эмоции.

📝 [Пройти опрос](http://localhost:3000/survey?tg_chat_id=987654321)
```

### **Type 2: Trend Alerts (Triggered by System)**

```python
# Called when anxiety/mood trend is detected
def send_trend_alert(user_id: UUID, trigger_type: str):
    # 1. Get user's notification preferences
    settings = UserSettingsRepository.get_by_user(user_id)
    
    # 2. Get recommendation based on trigger
    rec = RecommendationService.get_recommendation(user_id, trigger_type)
    
    # 3. Get user's chat_id
    user = UserRepository.get_by_id(user_id)
    chat_id = user.telegram_chat_id
    
    # 4. Send via preferred channel
    if settings.notify_channel in [TELEGRAM, BOTH] and chat_id:
        TelegramProvider.send_trend_notification(
            chat_id, 
            trigger_type, 
            rec.message
        )
    
    # 5. Log notification
    NotificationRepository.create_log(...)
```

**Message Example:**
```
⚠️ Внимание: Обнаружен рост тревожности

Мы заметили, что ваш уровень тревожности 
увеличился за последнюю неделю.

💡 Рекомендация: Попробуйте технику глубокого дыхания...
```

### **Type 3: Test Notification (Manual via API)**

```python
# API endpoint: PUT /api/v1/notifications/preferences
def send_test_notification(user_id: UUID):
    settings = UserSettingsRepository.get_by_user(user_id)
    user = UserRepository.get_by_id(user_id)
    
    message = "🔔 Это тестовое уведомление от Emotion Tracker"
    
    if settings.notify_channel in [TELEGRAM, BOTH] and user.telegram_chat_id:
        TelegramProvider.send_message(user.telegram_chat_id, message)
```

---

## ⚙️ Notification Preferences

### **Database Schema**

```sql
-- users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255),
    telegram_chat_id VARCHAR(255) NULL,  -- ← Links to Telegram
    ...
);

-- user_settings table
CREATE TABLE user_settings (
    user_id UUID PRIMARY KEY,
    notify_channel VARCHAR(50) DEFAULT 'email',  -- email|telegram|both
    reminders_enabled BOOLEAN DEFAULT TRUE,
    notify_window_start TIME NOT NULL,  -- e.g., 20:00
    notify_window_end TIME NOT NULL,    -- e.g., 22:00
    notify_frequency VARCHAR(50) DEFAULT 'daily',  -- daily|weekly|smart
    ...
);
```

### **Decision Logic**

```python
def should_send_notification(user, settings, notification_type):
    # Check if reminders are enabled
    if not settings.reminders_enabled:
        return False
    
    # Check notification type
    if notification_type == "trend_alert":
        # Trend alerts respect notify_channel
        if settings.notify_channel == "email":
            return has_email(user)
        elif settings.notify_channel == "telegram":
            return has_telegram(user)
        elif settings.notify_channel == "both":
            return True
    
    # Check time window for daily reminders
    if notification_type == "daily_reminder":
        if not is_within_window(
            settings.notify_window_start,
            settings.notify_window_end
        ):
            return False
    
    return True
```

---

## 🔌 Module Communication

### **Dependencies Graph**

```
API Layer (FastAPI routers)
    ↓ Depends(get_current_user), Depends(get_db)
Service Layer
    ├── UserService
    │   └── UserRepository, UserSettingsRepository, etc.
    ├── NotificationService
    │   ├── NotificationRepository
    │   ├── UserSettingsRepository
    │   ├── RecommendationService
    │   └── TelegramProvider (from core.clients)
    └── TelegramBotService
        ├── UserRepository
        ├── UserSettingsRepository
        └── MessageHandlers (message templates)
    ↓
Repository Layer
    └── Direct SQL queries via SQLAlchemy
    ↓
Database (PostgreSQL)
```

### **Example: Sending Daily Reminder**

```
1. Background Thread (TelegramBotService._check_and_send_reminders)
   ↓ queries
2. UserRepository + UserSettingsRepository
   ↓ returns
3. List of (User, UserSettings) tuples
   ↓ filters by
4. Current time == user's notify_window_start
   ↓ calls
5. TelegramBotService.send_reminder(chat_id)
   ↓ constructs
6. Message with survey URL
   ↓ sends via
7. HTTP POST to Telegram API
   ↓ logs
8. (Optional) NotificationLog in database
```

---

## 📁 File Structure

```
/app
├── services/
│   ├── bot/                    ← NEW LOCATION (was in /app/bot)
│   │   ├── __init__.py
│   │   ├── bot_service.py      ← Main bot logic + deep linking
│   │   └── handlers.py         ← Message templates
│   ├── user_service.py
│   ├── notification_service.py
│   ├── auth_service.py
│   └── recommendation_service.py
│
├── api/v1/
│   ├── users.py                ← User profile endpoints
│   ├── auth.py                 ← Login/register endpoints
│   └── notifications.py        ← Notification preferences
│
├── models/
│   ├── user.py                 ← User model with telegram_chat_id
│   └── notification.py         ← NotificationLog model
│
├── schemas/
│   ├── user.py                 ← UserResponse with telegram_chat_id
│   └── common.py               ← NotificationChannel enum
│
├── repositories/
│   ├── user_repo.py
│   ├── user_settings_repo.py
│   └── notification_repo.py
│
├── core/
│   ├── clients/
│   │   └── telegram_client.py  ← Low-level Telegram API client
│   └── config.py               ← Settings (BOT_TOKEN, FRONTEND_URL)
│
└── tasks/
    └── notifications.py        ← Celery tasks for background jobs
```

---

## 🚀 How to Start the Bot

```python
# In your main application startup code
from app.services.bot.bot_service import TelegramBotService
from app.core.database import SessionLocal
from app.core.config import settings

# Create database session
db = SessionLocal()

# Initialize bot service
bot_service = TelegramBotService(
    db=db,
    bot_token=settings.BOT_TOKEN,
    frontend_url=settings.FRONTEND_URL,  # http://localhost:3000
)

# Start bot in background thread
bot_service.start()

# Bot will now:
# 1. Poll Telegram for new messages
# 2. Handle /start, /help, /settings, /stop commands
# 3. Send daily reminders at configured times
```

---

## ✅ Summary

### **Before (Broken Logic):**
❌ Bot tried to find user by chat_id when user pressed /start  
❌ But chat_id was never linked to user in database  
❌ Chicken-and-egg problem!

### **After (Fixed Logic):**
✅ User registers on web app first (creates user record)  
✅ User clicks "Connect Telegram" on web app  
✅ Web app generates deep link with user_id  
✅ User opens link in Telegram → presses Start  
✅ Bot receives user_id from deep link  
✅ Bot links chat_id to existing user in database  
✅ Notifications work! 🎉

### **Key Files Changed:**
1. `/app/services/bot/bot_service.py` - Added `_handle_deep_link()` method
2. `/app/models/user.py` - Added `telegram_chat_id` field
3. `/app/schemas/user.py` - Added `telegram_chat_id` to UserResponse
4. `/app/services/user_service.py` - Returns `telegram_chat_id` in profile

All services now properly handle the `telegram_chat_id` field!
