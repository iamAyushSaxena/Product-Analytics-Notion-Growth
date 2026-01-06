
-- Revenue and Monetization Metrics
-- Calculates key revenue KPIs

WITH user_metrics AS (
    SELECT 
        DATE_TRUNC('month', u.signup_date) as cohort_month,
        COUNT(*) as total_users,
        SUM(CASE WHEN u.plan_type = 'paid' THEN 1 ELSE 0 END) as paid_users,
        SUM(CASE WHEN u.plan_type = 'paid' THEN 96 ELSE 0 END) as total_revenue
    FROM analytics.users u
    GROUP BY DATE_TRUNC('month', u.signup_date)
)

SELECT 
    cohort_month,
    total_users,
    paid_users,
    ROUND(100.0 * paid_users / total_users, 2) as conversion_rate_pct,
    total_revenue,
    ROUND(total_revenue / total_users, 2) as arpu,
    ROUND(total_revenue / NULLIF(paid_users, 0), 2) as arppu
FROM user_metrics
ORDER BY cohort_month DESC;
