
-- User Acquisition Funnel
-- Tracks users through key conversion stages

WITH user_stages AS (
    SELECT 
        u.user_id,
        u.signup_date,
        u.segment,
        u.acquisition_channel,
        
        -- Stage 1: Signup (all users)
        TRUE as has_signup,
        
        -- Stage 2: Activation (created first page)
        MAX(CASE WHEN e.event_type = 'page_created' THEN 1 ELSE 0 END) as has_activation,
        MIN(CASE WHEN e.event_type = 'page_created' THEN e.timestamp END) as activation_time,
        
        -- Stage 3: Engagement (3+ events in first week)
        SUM(CASE 
            WHEN e.timestamp <= u.signup_date + INTERVAL '7 days' 
            THEN 1 ELSE 0 
        END) as first_week_events,
        
        -- Stage 4: Collaboration (shared workspace)
        MAX(CASE WHEN e.event_type = 'workspace_shared' THEN 1 ELSE 0 END) as has_collaboration,
        
        -- Stage 5: Monetization (paid plan)
        MAX(CASE WHEN u.plan_type = 'paid' THEN 1 ELSE 0 END) as has_monetization
        
    FROM analytics.users u
    LEFT JOIN analytics.events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.signup_date, u.segment, u.acquisition_channel, u.plan_type
)

SELECT 
    'Signup' as stage,
    COUNT(*) as users,
    100.0 as pct_of_previous,
    100.0 as pct_of_total
FROM user_stages

UNION ALL

SELECT 
    'Activation' as stage,
    SUM(has_activation) as users,
    ROUND(100.0 * SUM(has_activation) / COUNT(*), 2) as pct_of_previous,
    ROUND(100.0 * SUM(has_activation) / (SELECT COUNT(*) FROM user_stages), 2) as pct_of_total
FROM user_stages

UNION ALL

SELECT 
    'Engagement' as stage,
    SUM(CASE WHEN first_week_events >= 3 THEN 1 ELSE 0 END) as users,
    ROUND(100.0 * SUM(CASE WHEN first_week_events >= 3 THEN 1 ELSE 0 END) / SUM(has_activation), 2) as pct_of_previous,
    ROUND(100.0 * SUM(CASE WHEN first_week_events >= 3 THEN 1 ELSE 0 END) / (SELECT COUNT(*) FROM user_stages), 2) as pct_of_total
FROM user_stages
WHERE has_activation = 1

UNION ALL

SELECT 
    'Collaboration' as stage,
    SUM(has_collaboration) as users,
    ROUND(100.0 * SUM(has_collaboration) / SUM(CASE WHEN first_week_events >= 3 THEN 1 ELSE 0 END), 2) as pct_of_previous,
    ROUND(100.0 * SUM(has_collaboration) / (SELECT COUNT(*) FROM user_stages), 2) as pct_of_total
FROM user_stages
WHERE first_week_events >= 3

UNION ALL

SELECT 
    'Monetization' as stage,
    SUM(has_monetization) as users,
    ROUND(100.0 * SUM(has_monetization) / SUM(has_collaboration), 2) as pct_of_previous,
    ROUND(100.0 * SUM(has_monetization) / (SELECT COUNT(*) FROM user_stages), 2) as pct_of_total
FROM user_stages
WHERE has_collaboration = 1

ORDER BY 
    CASE stage
        WHEN 'Signup' THEN 1
        WHEN 'Activation' THEN 2
        WHEN 'Engagement' THEN 3
        WHEN 'Collaboration' THEN 4
        WHEN 'Monetization' THEN 5
    END;
