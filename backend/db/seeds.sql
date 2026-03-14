-- Seed Data for Analytics Database
-- Insert sample data for testing

-- 1. Insert Queries
INSERT INTO queries (query_text, query_hash, complexity, intent, urgency, domain, user_id, session_id, created_at) VALUES 
('What is the capital of France?', 'hash1', 'SIMPLE', 'FACTUAL', 'FLEXIBLE', 'GENERAL', 'user1', 'session1', NOW() - INTERVAL '1 day'),
('Write a Python script to sort list', 'hash2', 'MEDIUM', 'CREATIVE', 'FLEXIBLE', 'TECH', 'user1', 'session1', NOW() - INTERVAL '23 hours'),
('Server is down, fix critical error', 'hash3', 'SIMPLE', 'TRANSACTIONAL', 'URGENT', 'TECH', 'user2', 'session2', NOW() - INTERVAL '2 hours');

-- 2. Insert Model Responses
INSERT INTO model_responses (query_id, model_name, response_text, tokens_used, latency_ms, cost, created_at) VALUES
(1, 'gpt-4-turbo', 'The capital of France is Paris.', 50, 450.5, 0.002, NOW() - INTERVAL '1 day'),
(2, 'claude-3-opus', 'Here is the sort script...', 200, 1200.0, 0.015, NOW() - INTERVAL '23 hours'),
(3, 'gpt-3.5-turbo', 'Checking logs...', 100, 300.0, 0.001, NOW() - INTERVAL '2 hours');

-- 3. Insert Carbon Metrics
INSERT INTO carbon_metrics (query_id, model_name, carbon_grams, energy_kwh, region, created_at) VALUES
(1, 'gpt-4-turbo', 0.5, 0.001, 'us-east-1', NOW() - INTERVAL '1 day'),
(2, 'claude-3-opus', 2.1, 0.005, 'us-west-2', NOW() - INTERVAL '23 hours'),
(3, 'gpt-3.5-turbo', 0.2, 0.0005, 'eu-central-1', NOW() - INTERVAL '2 hours');

-- 4. Insert Routing Decisions
INSERT INTO routing_decisions (id, query_id, selected_model, confidence_score, reasoning, created_at) VALUES
(1, 2, 'claude-3-opus', 0.95, 'Complex creative task requiring high capability', NOW() - INTERVAL '23 hours');

-- 5. Insert Cache Entries
INSERT INTO cache_entries (cache_key, query_hash, hit_count, last_accessed, expires_at) VALUES
('cache:hash1', 'hash1', 5, NOW(), NOW() + INTERVAL '1 hour');

-- 6. Insert RL Feedback
INSERT INTO rl_feedback (query_id, routing_decision_id, reward_score, feedback_type, user_satisfaction) VALUES
(2, 1, 0.9, 'explicit', 5.0);
