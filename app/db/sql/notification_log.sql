CREATE TABLE IF NOT EXISTS notification_log (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    recommendation_id UUID REFERENCES recommendations(id),
    channel VARCHAR(50) NOT NULL,
    trigger_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    delivery_status VARCHAR(20) NOT NULL DEFAULT 'queued',
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_notification_log_delivery_status CHECK (
        delivery_status IN ('queued', 'sent', 'failed', 'read')
    )
);

CREATE INDEX IF NOT EXISTS ix_notification_log_user_id ON notification_log (user_id);
CREATE INDEX IF NOT EXISTS ix_notification_log_delivery_status ON notification_log (delivery_status);
CREATE INDEX IF NOT EXISTS ix_notification_log_sent_at ON notification_log (sent_at);
