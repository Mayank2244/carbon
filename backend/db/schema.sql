-- Analytics Database Schema
-- Generated at 2026-01-09
-- 
-- Tables:
-- 1. queries: Stores user queries with classification metadata
-- 2. model_responses: AI responses linked to queries
-- 3. carbon_metrics: Carbon footprint data for each query
-- 4. routing_decisions: Which model was chosen and why
-- 5. cache_entries: Analytics on cache usage
-- 6. rl_feedback: User feedback for RL training

CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    complexity VARCHAR(20),
    intent VARCHAR(50),
    urgency VARCHAR(20),
    domain VARCHAR(50),
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    meta_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX ix_queries_query_hash ON queries (query_hash);
CREATE INDEX ix_queries_user_id ON queries (user_id);
CREATE INDEX ix_queries_created_at ON queries (created_at);
CREATE INDEX ix_queries_domain ON queries (domain);

CREATE TABLE model_responses (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id),
    model_name VARCHAR(100) NOT NULL,
    response_text TEXT NOT NULL,
    tokens_used INTEGER,
    latency_ms DOUBLE PRECISION,
    cost DOUBLE PRECISION,
    meta_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_model_responses_query_id ON model_responses (query_id);

CREATE TABLE carbon_metrics (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id),
    model_name VARCHAR(100) NOT NULL,
    carbon_grams DOUBLE PRECISION NOT NULL,
    energy_kwh DOUBLE PRECISION,
    region VARCHAR(50),
    meta_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_carbon_metrics_query_id ON carbon_metrics (query_id);
CREATE INDEX ix_carbon_metrics_created_at ON carbon_metrics (created_at);

CREATE TABLE routing_decisions (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id),
    selected_model VARCHAR(100) NOT NULL,
    confidence_score DOUBLE PRECISION,
    reasoning TEXT,
    alternative_models JSONB,
    meta_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_routing_decisions_query_id ON routing_decisions (query_id);

CREATE TABLE cache_entries (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL UNIQUE,
    query_hash VARCHAR(64) NOT NULL,
    hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    meta_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_cache_entries_query_hash ON cache_entries (query_hash);

CREATE TABLE rl_feedback (
    id SERIAL PRIMARY KEY,
    query_id INTEGER NOT NULL REFERENCES queries(id),
    routing_decision_id INTEGER NOT NULL REFERENCES routing_decisions(id),
    reward_score DOUBLE PRECISION NOT NULL,
    feedback_type VARCHAR(50),
    user_satisfaction DOUBLE PRECISION,
    meta_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_rl_feedback_query_id ON rl_feedback (query_id);
