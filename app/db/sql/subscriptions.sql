CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    plan VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'trial',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    provider VARCHAR(100),
    external_payment_id VARCHAR(255) UNIQUE,
    CONSTRAINT chk_subscriptions_status CHECK (
        status IN ('active', 'expired', 'canceled', 'trial')
    ),
    CONSTRAINT chk_subscriptions_period CHECK (
        expires_at IS NULL OR expires_at >= started_at
    )
);

CREATE INDEX IF NOT EXISTS ix_subscriptions_user_id ON subscriptions (user_id);
CREATE INDEX IF NOT EXISTS ix_subscriptions_status ON subscriptions (status);
