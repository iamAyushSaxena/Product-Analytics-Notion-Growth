
-- North Star Metric: Weekly Active Collaborative Workspaces
-- Measures engaged users with collaborative activity

WITH weekly_activity AS (
    SELECT 
        DATE_TRUNC('week', e.timestamp) as week,
        e.user_id,
        MAX(CASE WHEN e.event_type = 'workspace_shared' THEN 1 ELSE 0 END) as has_shared
    FROM analytics.events e
    WHERE e.timestamp >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY DATE_TRUNC('week', e.timestamp), e.user_id
)

SELECT 
    week,
    COUNT(DISTINCT user_id) as total_weekly_active_users,
    COUNT(DISTINCT CASE WHEN has_shared = 1 THEN user_id END) as weekly_active_collaborative_users,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN has_shared = 1 THEN user_id END) / 
          COUNT(DISTINCT user_id), 2) as collaboration_rate_pct
FROM weekly_activity
GROUP BY week
ORDER BY week DESC;
