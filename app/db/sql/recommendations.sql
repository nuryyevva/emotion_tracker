CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY,
    trigger_type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS ix_recommendations_trigger_type ON recommendations (trigger_type);
CREATE INDEX IF NOT EXISTS ix_recommendations_category ON recommendations (category);
CREATE INDEX IF NOT EXISTS ix_recommendations_is_active ON recommendations (is_active);
