CREATE TABLE IF NOT EXISTS emotion_records (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    record_date DATE NOT NULL,
    mood SMALLINT NOT NULL,
    anxiety SMALLINT NOT NULL,
    fatigue SMALLINT NOT NULL,
    sleep_hours NUMERIC(3,1),
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_emotion_records_user_date UNIQUE (user_id, record_date),
    CONSTRAINT chk_emotion_records_mood CHECK (mood BETWEEN 1 AND 10),
    CONSTRAINT chk_emotion_records_anxiety CHECK (anxiety BETWEEN 1 AND 10),
    CONSTRAINT chk_emotion_records_fatigue CHECK (fatigue BETWEEN 1 AND 10),
    CONSTRAINT chk_emotion_records_sleep_hours CHECK (
        sleep_hours IS NULL OR sleep_hours BETWEEN 0 AND 24
    )
);

CREATE INDEX IF NOT EXISTS ix_emotion_records_user_id ON emotion_records (user_id);
CREATE INDEX IF NOT EXISTS ix_emotion_records_record_date ON emotion_records (record_date);
