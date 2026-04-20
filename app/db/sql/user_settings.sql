CREATE TABLE IF NOT EXISTS user_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    weekday_wake_up TIME NOT NULL,
    weekday_bedtime TIME NOT NULL,
    weekend_wake_up TIME NOT NULL,
    weekend_bedtime TIME NOT NULL,
    notify_channel VARCHAR(20) NOT NULL DEFAULT 'email',
    notify_window_start TIME NOT NULL,
    notify_window_end TIME NOT NULL,
    notify_frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
    reminders_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_user_settings_notify_channel CHECK (notify_channel IN ('email', 'telegram', 'both')),
    CONSTRAINT chk_user_settings_notify_frequency CHECK (notify_frequency IN ('daily', 'weekly', 'smart')),
    CONSTRAINT chk_user_settings_notify_window CHECK (notify_window_end > notify_window_start)
);
