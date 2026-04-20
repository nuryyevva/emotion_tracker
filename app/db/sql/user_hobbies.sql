CREATE TABLE IF NOT EXISTS user_hobbies (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    hobby VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_hobbies_user_hobby UNIQUE (user_id, hobby)
);

CREATE INDEX IF NOT EXISTS ix_user_hobbies_user_id ON user_hobbies (user_id);
