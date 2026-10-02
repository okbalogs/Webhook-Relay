-- Webhook Relay Database Initialization Script

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types
DO $$ BEGIN
    CREATE TYPE provider_type AS ENUM ('stripe', 'github', 'shopify', 'generic');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE delivery_status AS ENUM ('pending', 'success', 'failed', 'retrying', 'exhausted');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Endpoints Table
CREATE TABLE IF NOT EXISTS endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    secret_key VARCHAR(255) NOT NULL,
    provider provider_type NOT NULL DEFAULT 'generic',
    target_url VARCHAR(1024) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    max_retries INT NOT NULL DEFAULT 5,
    timeout_seconds INT NOT NULL DEFAULT 10,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partitioned Ingested Webhook Events Table
CREATE TABLE IF NOT EXISTS events (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    endpoint_id UUID NOT NULL REFERENCES endpoints(id) ON DELETE CASCADE,
    provider provider_type NOT NULL,
    event_type VARCHAR(255),
    headers JSONB NOT NULL,
    payload JSONB NOT NULL,
    raw_body TEXT NOT NULL,
    signature_valid BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Monthly partitions for 2026 and 2027
CREATE TABLE IF NOT EXISTS events_2026_10 PARTITION OF events
    FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2026-11-01 00:00:00+00');

CREATE TABLE IF NOT EXISTS events_2026_11 PARTITION OF events
    FOR VALUES FROM ('2026-11-01 00:00:00+00') TO ('2026-12-01 00:00:00+00');

CREATE TABLE IF NOT EXISTS events_2026_12 PARTITION OF events
    FOR VALUES FROM ('2026-12-01 00:00:00+00') TO ('2027-01-01 00:00:00+00');

CREATE TABLE IF NOT EXISTS events_default PARTITION OF events DEFAULT;

-- Delivery Attempts Table
CREATE TABLE IF NOT EXISTS delivery_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL,
    event_created_at TIMESTAMPTZ NOT NULL,
    endpoint_id UUID NOT NULL REFERENCES endpoints(id) ON DELETE CASCADE,
    attempt_count INT NOT NULL DEFAULT 1,
    status delivery_status NOT NULL DEFAULT 'pending',
    response_status INT,
    response_headers JSONB,
    response_body TEXT,
    execution_duration_ms INT,
    error_message TEXT,
    next_retry_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- PARTIAL INDEX: High performance query for pending and retrying webhook delivery workers
CREATE INDEX IF NOT EXISTS idx_delivery_pending_retries 
ON delivery_attempts (next_retry_at, status) 
WHERE status IN ('pending', 'retrying');

-- Event lookup index
CREATE INDEX IF NOT EXISTS idx_events_endpoint_created 
ON events (endpoint_id, created_at DESC);

