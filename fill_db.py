# seed_db.py
import os
import random
import uuid
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# ⚠️ ADJUST THESE IMPORTS TO MATCH YOUR ACTUAL PROJECT STRUCTURE
from app.models import (
    User, UserSettings, EmotionRecord, UserHobby, UserCopingMethod,
    Subscription, Recommendation, NotificationLog
)
from app.schemas.common import (
    NotificationChannel, SubscriptionStatus, DeliveryStatus,
    UserStatus, NotifyFrequency
)

# Load environment variables (falls back to defaults if not set)
DB_USER = os.getenv("POSTGRES_USER", "emotion_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "emotion_password")
DB_NAME = os.getenv("POSTGRES_DB", "emotion_tracker")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)


def run_seeder(num_users: int = 10, days_back: int = 30, fresh: bool = True):
    """
    Seed the database with random test data.

    Args:
        num_users: Number of users to create
        days_back: How many days of emotion records to generate
        fresh: If True, clear existing data first (development only!)
    """
    print("🌱 Starting database seed...")

    # Create tables if they don't exist (for initial setup)
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:

        # 🧹 Optional: Clear existing data for a clean slate (development only!)
        if fresh:
            print("🗑️  Clearing existing data...")
            session.execute(text("""
                TRUNCATE TABLE 
                    notification_log, 
                    subscriptions, 
                    emotion_records, 
                    user_coping_methods, 
                    user_hobbies, 
                    user_settings, 
                    recommendations, 
                    users 
                CASCADE
            """))
            session.commit()

        # 1. Create Users
        users = []
        for i in range(num_users):
            user = User(
                id=uuid.uuid4(),
                email=f"test_user_{i + 1}@example.com",
                password_hash=f"fake_hash_{uuid.uuid4().hex}",
                timezone=random.choice(["UTC", "Europe/Moscow", "Asia/Ashgabat", "America/New_York"]),
                telegram_chat_id=f"{random.randint(100000000, 999999999)}" if random.random() > 0.3 else None,
                status=UserStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            users.append(user)
        session.add_all(users)

        # 2. User Settings (Constraint: notify_window_end > notify_window_start)
        settings_list = []
        for user in users:
            start_h = random.randint(7, 9)
            settings = UserSettings(
                user_id=user.id,
                weekday_wake_up=time(start_h, 0),
                weekday_bedtime=time(random.randint(22, 23), random.randint(0, 59)),
                weekend_wake_up=time(start_h + 1, 0),
                weekend_bedtime=time(23, 30),
                notify_window_start=time(8, 0),
                notify_window_end=time(20, 0),  # Guaranteed > start
                notify_channel=random.choice(list(NotificationChannel)),
                notify_frequency=random.choice(list(NotifyFrequency)),
                reminders_enabled=True,
                updated_at=datetime.now()
            )
            settings_list.append(settings)
        session.add_all(settings_list)

        # 3. Hobbies & Coping Methods ✅ FIXED: Use random.sample() for uniqueness
        hobbies_pool = ["Reading", "Sports", "Gaming", "Cooking", "Music", "Hiking", "Photography", "Coding"]
        coping_pool = ["Deep Breathing", "Meditation", "Journaling", "Exercise", "Talking to a friend",
                       "Listening to music"]

        hobbies = []
        for user in users:
            # Pick 1-3 UNIQUE hobbies per user
            num_hobbies = random.randint(1, min(3, len(hobbies_pool)))
            for hobby in random.sample(hobbies_pool, num_hobbies):
                hobbies.append(UserHobby(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    hobby=hobby
                ))

        coping_methods = []
        for user in users:
            # Pick 1-2 UNIQUE coping methods per user
            num_methods = random.randint(1, min(2, len(coping_pool)))
            for method in random.sample(coping_pool, num_methods):
                coping_methods.append(UserCopingMethod(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    method=method
                ))
        session.add_all(hobbies + coping_methods)

        # 4. Emotion Records (Constraints: 1-10 metrics, 0-24 sleep, unique user+date)
        emotion_records = []
        for user in users:
            used_dates = set()
            today = date.today()
            for _ in range(random.randint(10, days_back)):
                rec_date = today - timedelta(days=random.randint(0, days_back - 1))
                if rec_date in used_dates:
                    continue
                used_dates.add(rec_date)

                sleep = Decimal(str(round(random.uniform(0, 24), 1))) if random.random() > 0.1 else None

                emotion_records.append(EmotionRecord(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    record_date=rec_date,
                    mood=random.randint(1, 10),
                    anxiety=random.randint(1, 10),
                    fatigue=random.randint(1, 10),
                    sleep_hours=sleep,
                    note=f"Auto-generated log for {rec_date}" if random.random() > 0.7 else None,
                    created_at=datetime.now()
                ))
        session.add_all(emotion_records)

        # 5. Recommendations
        recs = [
            Recommendation(id=uuid.uuid4(), trigger_type="fatigue_high", category="rest",
                           message="Try taking a 20-min power nap.", priority=5),
            Recommendation(id=uuid.uuid4(), trigger_type="anxiety_high", category="mindfulness",
                           message="Practice 5 minutes of box breathing.", priority=8),
            Recommendation(id=uuid.uuid4(), trigger_type="mood_low", category="activity",
                           message="Go for a short walk outside.", priority=6),
            Recommendation(id=uuid.uuid4(), trigger_type="sleep_deviation", category="routine",
                           message="Stick to your usual bedtime tonight.", priority=4),
            Recommendation(id=uuid.uuid4(), trigger_type="mood_improvement", category="positive",
                           message="Great progress! Keep up the routine.", priority=2),
        ]
        session.add_all(recs)
        session.flush()  # Ensure IDs are assigned before linking logs

        # 6. Subscriptions (Constraint: expires_at >= started_at OR NULL)
        subs = []
        for user in users:
            started = datetime.now() - timedelta(days=random.randint(1, 100))
            expires = started + timedelta(days=random.randint(30, 365)) if random.random() > 0.2 else None
            subs.append(Subscription(
                id=uuid.uuid4(),
                user_id=user.id,
                plan=random.choice(["free", "pro"]),
                status=random.choice(list(SubscriptionStatus)),
                started_at=started,
                expires_at=expires,
                provider="stripe" if random.random() > 0.4 else None
            ))
        session.add_all(subs)

        # 7. Notification Logs
        logs = []
        for user in users:
            for _ in range(random.randint(0, 4)):
                rec = random.choice(recs)
                logs.append(NotificationLog(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    recommendation_id=rec.id,
                    channel=random.choice(list(NotificationChannel)).value,  # String column
                    trigger_type=rec.trigger_type,
                    message=rec.message,
                    delivery_status=random.choice(list(DeliveryStatus)),  # Enum column
                    sent_at=datetime.now() - timedelta(hours=random.randint(0, 48))
                ))
        session.add_all(logs)

        # Commit everything
        session.commit()
        print(
            f"✅ Successfully seeded {num_users} users with {len(emotion_records)} emotion records, {len(logs)} notifications, and related data.")


if __name__ == "__main__":
    # Run with 15 users, 30 days of history, and fresh data
    run_seeder(num_users=15, days_back=30, fresh=True)
