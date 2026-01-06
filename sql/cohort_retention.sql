
-- Cohort Retention Analysis
-- Calculates retention rates by signup cohort

WITH user_cohorts AS (
    SELECT 
        user_id,
        DATE_TRUNC('month', signup_date) as cohort_month,
        signup_date
    FROM analytics.users
),

user_activity AS (
    SELECT 
        uc.user_id,
        uc.cohort_month,
        DATE_TRUNC('month', e.timestamp) as activity_month,
        EXTRACT(MONTH FROM AGE(e.timestamp, uc.signup_date)) as months_since_signup
    FROM user_cohorts uc
    JOIN analytics.events e ON uc.user_id = e.user_id
    GROUP BY uc.user_id, uc.cohort_month, activity_month, months_since_signup
),

cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT user_id) as cohort_size
    FROM user_cohorts
    GROUP BY cohort_month
),

retention_data AS (
    SELECT 
        ua.cohort_month,
        ua.months_since_signup,
        COUNT(DISTINCT ua.user_id) as active_users
    FROM user_activity ua
    GROUP BY ua.cohort_month, ua.months_since_signup
)

SELECT 
    rd.cohort_month,
    cs.cohort_size,
    rd.months_since_signup,
    rd.active_users,
    ROUND(100.0 * rd.active_users / cs.cohort_size, 2) as retention_pct
FROM retention_data rd
JOIN cohort_sizes cs ON rd.cohort_month = cs.cohort_month
WHERE rd.months_since_signup BETWEEN 0 AND 12
ORDER BY rd.cohort_month, rd.months_since_signup;
