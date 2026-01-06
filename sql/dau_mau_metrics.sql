
-- Daily Active Users (DAU)
-- Counts unique users who performed any action on a given date

SELECT 
    DATE(timestamp) as activity_date,
    COUNT(DISTINCT user_id) as dau,
    COUNT(*) as total_events,
    COUNT(*) / COUNT(DISTINCT user_id) as avg_events_per_user
FROM analytics.events
WHERE DATE(timestamp) = CURRENT_DATE
GROUP BY activity_date
ORDER BY activity_date DESC;



-- Monthly Active Users (MAU)
-- Counts unique users active in the last 30 days

SELECT 
    DATE(CURRENT_DATE) as reference_date,
    COUNT(DISTINCT user_id) as mau,
    COUNT(*) as total_events,
    COUNT(DISTINCT DATE(timestamp)) as active_days
FROM analytics.events
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
  AND timestamp <= CURRENT_DATE
GROUP BY reference_date;
