CREATE TABLE IF NOT EXISTS user_coping_methods (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    method VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_coping_methods_user_method UNIQUE (user_id, method)
);

CREATE INDEX IF NOT EXISTS ix_user_coping_methods_user_id ON user_coping_methods (user_id);
