"""
SQL Query Templates
Production-ready SQL queries for analytics database
"""

from typing import Dict, List
from config import *


class SQLQueryGenerator:
    """
    Generates SQL queries for product analytics
    """
    
    def __init__(self, schema: str = SCHEMA_NAME):
        """
        Initialize query generator
        
        Args:
            schema: Database schema name
        """
        self.schema = schema
    
    def get_dau_query(self, date: str = 'CURRENT_DATE') -> str:
        """
        Generate DAU calculation query
        
        Args:
            date: Date to calculate DAU for
            
        Returns:
            SQL query string
        """
        query = f"""
-- Daily Active Users (DAU)
-- Counts unique users who performed any action on a given date

SELECT 
    DATE(timestamp) as activity_date,
    COUNT(DISTINCT user_id) as dau,
    COUNT(*) as total_events,
    COUNT(*) / COUNT(DISTINCT user_id) as avg_events_per_user
FROM {self.schema}.events
WHERE DATE(timestamp) = {date}
GROUP BY activity_date
ORDER BY activity_date DESC;
"""
        return query
    
    def get_mau_query(self, date: str = 'CURRENT_DATE') -> str:
        """
        Generate MAU calculation query
        
        Args:
            date: Date to calculate MAU for
            
        Returns:
            SQL query string
        """
        query = f"""
-- Monthly Active Users (MAU)
-- Counts unique users active in the last 30 days

SELECT 
    DATE({date}) as reference_date,
    COUNT(DISTINCT user_id) as mau,
    COUNT(*) as total_events,
    COUNT(DISTINCT DATE(timestamp)) as active_days
FROM {self.schema}.events
WHERE timestamp >= {date} - INTERVAL '30 days'
  AND timestamp <= {date}
GROUP BY reference_date;
"""
        return query
    
    def get_funnel_query(self) -> str:
        """
        Generate user funnel analysis query
        
        Returns:
            SQL query string
        """
        query = f"""
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
        
    FROM {self.schema}.users u
    LEFT JOIN {self.schema}.events e ON u.user_id = e.user_id
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
"""
        return query
    
    def get_cohort_retention_query(self) -> str:
        """
        Generate cohort retention analysis query
        
        Returns:
            SQL query string
        """
        query = f"""
-- Cohort Retention Analysis
-- Calculates retention rates by signup cohort

WITH user_cohorts AS (
    SELECT 
        user_id,
        DATE_TRUNC('month', signup_date) as cohort_month,
        signup_date
    FROM {self.schema}.users
),

user_activity AS (
    SELECT 
        uc.user_id,
        uc.cohort_month,
        DATE_TRUNC('month', e.timestamp) as activity_month,
        EXTRACT(MONTH FROM AGE(e.timestamp, uc.signup_date)) as months_since_signup
    FROM user_cohorts uc
    JOIN {self.schema}.events e ON uc.user_id = e.user_id
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
"""
        return query
    
    def get_power_users_query(self, top_percentile: float = 0.10) -> str:
        """
        Generate power users identification query
        
        Args:
            top_percentile: Top % to classify as power users
            
        Returns:
            SQL query string
        """
        query = f"""
-- Power Users Identification
-- Identifies most engaged users (top {top_percentile*100}%)

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
        
    FROM {self.schema}.users u
    LEFT JOIN {self.schema}.events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.segment, u.plan_type
),

engagement_percentiles AS (
    SELECT 
        PERCENTILE_CONT({1 - top_percentile}) WITHIN GROUP (ORDER BY events_per_active_day) as threshold
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
"""
        return query
    
    def get_feature_adoption_query(self) -> str:
        """
        Generate feature adoption analysis query
        
        Returns:
            SQL query string
        """
        query = f"""
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
    FROM {self.schema}.events e
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
    FROM {self.schema}.users
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
"""
        return query
    
    def get_revenue_metrics_query(self) -> str:
        """
        Generate revenue and monetization metrics query
        
        Returns:
            SQL query string
        """
        query = f"""
-- Revenue and Monetization Metrics
-- Calculates key revenue KPIs

WITH user_metrics AS (
    SELECT 
        DATE_TRUNC('month', u.signup_date) as cohort_month,
        COUNT(*) as total_users,
        SUM(CASE WHEN u.plan_type = 'paid' THEN 1 ELSE 0 END) as paid_users,
        SUM(CASE WHEN u.plan_type = 'paid' THEN {AVERAGE_REVENUE_PER_USER} ELSE 0 END) as total_revenue
    FROM {self.schema}.users u
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
"""
        return query
    
    def get_north_star_metric_query(self) -> str:
        """
        Generate North Star metric calculation query
        
        Returns:
            SQL query string
        """
        query = f"""
-- North Star Metric: Weekly Active Collaborative Workspaces
-- Measures engaged users with collaborative activity

WITH weekly_activity AS (
    SELECT 
        DATE_TRUNC('week', e.timestamp) as week,
        e.user_id,
        MAX(CASE WHEN e.event_type = 'workspace_shared' THEN 1 ELSE 0 END) as has_shared
    FROM {self.schema}.events e
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
"""
        return query
    
    def save_all_queries(self, output_dir: Path = SQL_DIR):
        """
        Save all queries to SQL files
        
        Args:
            output_dir: Directory to save SQL files
        """
        print(f"📊 Saving SQL queries to {output_dir}...")
        
        queries = {
            'dau_mau_metrics.sql': self.get_dau_query() + "\n\n" + self.get_mau_query(),
            'funnel_analysis.sql': self.get_funnel_query(),
            'cohort_retention.sql': self.get_cohort_retention_query(),
            'power_users.sql': self.get_power_users_query(),
            'feature_adoption.sql': self.get_feature_adoption_query(),
            'revenue_metrics.sql': self.get_revenue_metrics_query(),
            'north_star_metric.sql': self.get_north_star_metric_query()
        }
        
        for filename, query in queries.items():
            filepath = output_dir / filename
            with open(filepath, 'w') as f:
                f.write(query)
            print(f"✅ Saved: {filename}")
        
        print(f"✅ All queries saved to {output_dir}")


if __name__ == "__main__":
    print("=" * 80)
    print(" SQL QUERY GENERATOR")
    print("=" * 80)
    print()
    
    generator = SQLQueryGenerator()
    
    print("\n--- GENERATING SQL QUERIES ---\n")
    
    print("1. DAU Query:")
    print(generator.get_dau_query())
    
    print("\n2. Funnel Query:")
    print(generator.get_funnel_query()[:500] + "...\n")
    
    print("\n3. North Star Metric Query:")
    print(generator.get_north_star_metric_query()[:500] + "...\n")
    
    # Save all queries
    generator.save_all_queries()