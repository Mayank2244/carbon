-- Analytics Queries Examples
-- Common queries for analyzing CarbonSense performance

-- 1. Daily Carbon Savings (Assuming hypothetical baseline vs actual)
-- Note: 'savings' would be calculated vs a baseline model logic, here we just show daily totals
SELECT 
    DATE(created_at) as log_date,
    COUNT(*) as total_queries,
    SUM(carbon_grams) as total_carbon_emitted_g,
    AVG(carbon_grams) as avg_carbon_per_query_g
FROM carbon_metrics
GROUP BY DATE(created_at)
ORDER BY log_date DESC;

-- 2. Model Usage Distribution
SELECT 
    model_name,
    COUNT(*) as usage_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM model_responses
GROUP BY model_name
ORDER BY usage_count DESC;

-- 3. Cache Hit Rate Trends
SELECT 
    DATE(last_accessed) as access_date,
    SUM(hit_count) as total_hits,
    COUNT(DISTINCT query_hash) as unique_cached_queries
FROM cache_entries
GROUP BY DATE(last_accessed)
ORDER BY access_date DESC;

-- 4. Average Response Time by Complexity
SELECT 
    q.complexity,
    COUNT(*) as query_count,
    ROUND(AVG(mr.latency_ms)::numeric, 2) as avg_latency_ms,
    ROUND(AVG(mr.tokens_used)::numeric, 2) as avg_tokens
FROM queries q
JOIN model_responses mr ON q.id = mr.query_id
WHERE q.complexity IS NOT NULL
GROUP BY q.complexity
ORDER BY avg_latency_ms DESC;

-- 5. Query Intent Distribution
SELECT 
    intent,
    COUNT(*) as count
FROM queries
WHERE intent IS NOT NULL
GROUP BY intent;

-- 6. Top 5 Most Expensive Queries (by Carbon)
SELECT 
    q.query_text,
    cm.carbon_grams,
    cm.model_name
FROM carbon_metrics cm
JOIN queries q ON cm.query_id = q.id
ORDER BY cm.carbon_grams DESC
LIMIT 5;
