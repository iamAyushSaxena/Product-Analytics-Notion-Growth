
-- Feature Adoption Analysis
-- Tracks adoption and usage frequency of key features

WITH feature_usage AS (
    SELECT 
        e.event_type as feature,
        COUNT(DISTINCT e.user_id) as users_adopted,
        COUNT(*) as total_usage,
        COUNT(*) / NULLIF(COUNT(DISTINCT e.user_id), 0) as avg_usage_per_user,
        MIN(e.timestamp) as first_used,
        MAX(e.timestamp) as last_used
    FROM analytics.events e
    WHERE e.event_type IN (
        'page_created',
        'content_edited',
        'workspace_shared',
        'search_performed',
        'page_viewed'
    )
    GROUP BY e.event_type
),

total_users AS (
    SELECT COUNT(DISTINCT user_id) as total
    FROM analytics.users
)

SELECT 
    fu.feature,
    fu.users_adopted,
    ROUND(100.0 * fu.users_adopted / tu.total, 2) as adoption_rate_pct,
    fu.total_usage,
    ROUND(fu.avg_usage_per_user, 2) as avg_uses_per_adopter,
    fu.first_used,
    fu.last_used
FROM feature_usage fu
CROSS JOIN total_users tu
ORDER BY fu.users_adopted DESC;
