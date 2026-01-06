
-- Power Users Identification
-- Identifies most engaged users (top 10.0%)

WITH user_activity_metrics AS (
    SELECT 
        u.user_id,
        u.segment,
        u.plan_type,
        COUNT(*) as total_events,
        COUNT(DISTINCT DATE(e.timestamp)) as active_days,
        MAX(e.timestamp) as last_activity,
        COUNT(*) / NULLIF(COUNT(DISTINCT DATE(e.timestamp)), 0) as events_per_active_day,
        
        -- Feature usage
        SUM(CASE WHEN e.event_type = 'page_created' THEN 1 ELSE 0 END) as pages_created,
        SUM(CASE WHEN e.event_type = 'workspace_shared' THEN 1 ELSE 0 END) as workspaces_shared,
        SUM(CASE WHEN e.event_type = 'content_edited' THEN 1 ELSE 0 END) as edits_made
        
    FROM analytics.users u
    LEFT JOIN analytics.events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.segment, u.plan_type
),

engagement_percentiles AS (
    SELECT 
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY events_per_active_day) as threshold
    FROM user_activity_metrics
)

SELECT 
    uam.*,
    CASE 
        WHEN uam.events_per_active_day >= ep.threshold THEN 'power_user'
        ELSE 'casual_user'
    END as user_type,
    ROUND(uam.events_per_active_day, 2) as engagement_score
FROM user_activity_metrics uam
CROSS JOIN engagement_percentiles ep
WHERE uam.total_events > 0
ORDER BY uam.events_per_active_day DESC;
