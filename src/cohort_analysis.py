"""
Cohort Analysis Module
Analyzes user retention and cohort behavior over time
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from config import *


class CohortAnalyzer:
    """
    Performs cohort-based retention and behavior analysis
    """
    
    def __init__(self, users_df: pd.DataFrame, events_df: pd.DataFrame):
        """
        Initialize cohort analyzer
        
        Args:
            users_df: User profiles DataFrame
            events_df: Events DataFrame
        """
        self.users_df = users_df
        self.events_df = events_df
        
        # Ensure timestamp is datetime
        self.events_df['timestamp'] = pd.to_datetime(self.events_df['timestamp'])
        self.users_df['signup_date'] = pd.to_datetime(self.users_df['signup_date'])
    
    def create_cohorts(self, period: str = 'monthly') -> pd.DataFrame:
        """
        Create user cohorts based on signup date
        
        Args:
            period: Cohort period ('weekly', 'monthly', 'quarterly')
            
        Returns:
            DataFrame with cohort assignments
        """
        print(f"📊 Creating {period} cohorts...")
        
        cohorts = self.users_df.copy()
        
        if period == 'weekly':
            cohorts['cohort'] = cohorts['signup_date'].dt.to_period('W')
        elif period == 'monthly':
            cohorts['cohort'] = cohorts['signup_date'].dt.to_period('M')
        elif period == 'quarterly':
            cohorts['cohort'] = cohorts['signup_date'].dt.to_period('Q')
        
        cohorts['cohort_date'] = cohorts['cohort'].dt.start_time
        
        print(f"✅ Created {cohorts['cohort'].nunique()} cohorts")
        return cohorts
    
    def calculate_retention(self, cohorts_df: pd.DataFrame,
                          period: str = 'monthly') -> pd.DataFrame:
        """
        Calculate retention rates for each cohort
        
        Args:
            cohorts_df: DataFrame from create_cohorts()
            period: Analysis period
            
        Returns:
            DataFrame with retention matrix
        """
        print(f"📊 Calculating {period} retention rates...")
        
        # Merge user cohorts with events
        user_cohorts = cohorts_df[['user_id', 'cohort', 'cohort_date']].copy()
        events_with_cohort = self.events_df.merge(user_cohorts, on='user_id')
        
        # Calculate period since cohort for each event
        if period == 'weekly':
            events_with_cohort['event_period'] = events_with_cohort['timestamp'].dt.to_period('W')
        elif period == 'monthly':
            events_with_cohort['event_period'] = events_with_cohort['timestamp'].dt.to_period('M')
        
        events_with_cohort['periods_since_cohort'] = (
            events_with_cohort['event_period'] - events_with_cohort['cohort']
        ).apply(lambda x: x.n)
        
        # Calculate retention: users active in each period
        retention = events_with_cohort.groupby(
            ['cohort', 'periods_since_cohort']
        )['user_id'].nunique().reset_index()
        
        retention.columns = ['cohort', 'period', 'active_users']
        
        # Get cohort sizes (period 0)
        cohort_sizes = retention[retention['period'] == 0][['cohort', 'active_users']].copy()
        cohort_sizes.columns = ['cohort', 'cohort_size']
        
        # Calculate retention rate
        retention = retention.merge(cohort_sizes, on='cohort')
        retention['retention_rate'] = retention['active_users'] / retention['cohort_size']
        
        print("✅ Calculated retention rates")
        return retention
    
    def create_retention_matrix(self, retention_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create retention matrix (cohort table format)
        
        Args:
            retention_df: DataFrame from calculate_retention()
            
        Returns:
            Pivot table with retention matrix
        """
        print("📊 Creating retention matrix...")
        
        # Pivot to matrix format
        matrix = retention_df.pivot(
            index='cohort',
            columns='period',
            values='retention_rate'
        ).fillna(0)
        
        # Convert to percentage
        matrix = (matrix * 100).round(2)
        
        print("✅ Created retention matrix")
        return matrix
    
    def calculate_cohort_ltv(self, cohorts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Lifetime Value (LTV) by cohort
        
        Args:
            cohorts_df: DataFrame from create_cohorts()
            
        Returns:
            DataFrame with LTV metrics by cohort
        """
        print("📊 Calculating cohort LTV...")
        
        # Get paid users and their cohorts
        paid_users = cohorts_df[cohorts_df['plan_type'] == 'paid'].copy()
        
        # Calculate LTV metrics by cohort
        ltv_metrics = paid_users.groupby('cohort').agg({
            'user_id': 'count'
        }).reset_index()
        ltv_metrics.columns = ['cohort', 'paid_users']
        
        # Get total cohort sizes
        cohort_sizes = cohorts_df.groupby('cohort')['user_id'].count().reset_index()
        cohort_sizes.columns = ['cohort', 'total_users']
        
        # Merge and calculate conversion rate
        ltv_metrics = ltv_metrics.merge(cohort_sizes, on='cohort')
        ltv_metrics['conversion_rate'] = ltv_metrics['paid_users'] / ltv_metrics['total_users']
        
        # Calculate revenue (assuming AVERAGE_REVENUE_PER_USER)
        ltv_metrics['estimated_revenue'] = ltv_metrics['paid_users'] * AVERAGE_REVENUE_PER_USER
        ltv_metrics['revenue_per_user'] = ltv_metrics['estimated_revenue'] / ltv_metrics['total_users']
        
        # Calculate payback period (simplified)
        # Assuming CAC of $50
        assumed_cac = 50
        ltv_metrics['payback_months'] = assumed_cac / (ltv_metrics['revenue_per_user'] / 12)
        
        print("✅ Calculated cohort LTV")
        return ltv_metrics
    
    def analyze_cohort_behavior(self, cohorts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze behavioral differences between cohorts
        
        Args:
            cohorts_df: DataFrame from create_cohorts()
            
        Returns:
            DataFrame with cohort behavior metrics
        """
        print("📊 Analyzing cohort behavior...")
        
        # Merge events with cohorts
        events_with_cohort = self.events_df.merge(
            cohorts_df[['user_id', 'cohort']], on='user_id'
        )
        
        # Calculate behavior metrics by cohort
        behavior_metrics = events_with_cohort.groupby('cohort').agg({
            'user_id': 'nunique',
            'event_type': 'count'
        }).reset_index()
        behavior_metrics.columns = ['cohort', 'active_users', 'total_events']
        
        # Events per user
        behavior_metrics['events_per_user'] = (
            behavior_metrics['total_events'] / behavior_metrics['active_users']
        )
        
        # Calculate feature usage by cohort
        collaboration_users = events_with_cohort[
            events_with_cohort['event_type'] == 'workspace_shared'
        ].groupby('cohort')['user_id'].nunique().reset_index()
        collaboration_users.columns = ['cohort', 'collaborative_users']
        
        behavior_metrics = behavior_metrics.merge(collaboration_users, on='cohort', how='left')
        behavior_metrics['collaboration_rate'] = (
            behavior_metrics['collaborative_users'] / behavior_metrics['active_users']
        )
        
        print("✅ Analyzed cohort behavior")
        return behavior_metrics
    
    def compare_early_vs_late_cohorts(self, cohorts_df: pd.DataFrame,
                                     retention_df: pd.DataFrame) -> Dict:
        """
        Compare retention between early and late cohorts
        
        Args:
            cohorts_df: DataFrame from create_cohorts()
            retention_df: DataFrame from calculate_retention()
            
        Returns:
            Dictionary with comparison metrics
        """
        print("📊 Comparing early vs late cohorts...")
        
        # Sort cohorts by date
        cohorts_sorted = sorted(cohorts_df['cohort'].unique())
        
        # Split into early (first 25%) and late (last 25%)
        split_point = len(cohorts_sorted) // 4
        early_cohorts = cohorts_sorted[:split_point]
        late_cohorts = cohorts_sorted[-split_point:]
        
        # Calculate average retention for each group
        early_retention = retention_df[
            retention_df['cohort'].isin(early_cohorts)
        ].groupby('period')['retention_rate'].mean()
        
        late_retention = retention_df[
            retention_df['cohort'].isin(late_cohorts)
        ].groupby('period')['retention_rate'].mean()
        
        comparison = {
            'early_cohorts': [str(c) for c in early_cohorts],
            'late_cohorts': [str(c) for c in late_cohorts],
            'early_retention_day30': early_retention.get(1, 0) if len(early_retention) > 1 else 0,
            'late_retention_day30': late_retention.get(1, 0) if len(late_retention) > 1 else 0,
            'improvement': (
                late_retention.get(1, 0) - early_retention.get(1, 0)
            ) if len(early_retention) > 1 and len(late_retention) > 1 else 0
        }
        
        print(f"✅ Early cohort retention (Month 1): {comparison['early_retention_day30']*100:.1f}%")
        print(f"✅ Late cohort retention (Month 1): {comparison['late_retention_day30']*100:.1f}%")
        print(f"✅ Improvement: {comparison['improvement']*100:.1f} percentage points")
        
        return comparison
    
    def calculate_day_n_retention(self, cohorts_df: pd.DataFrame,
                                  days: List[int] = [1, 7, 14, 30, 60, 90]) -> pd.DataFrame:
        """
        Calculate Day-N retention - Optimized for performance
        """
        print(f"📊 Calculating Day-N retention for days: {days}...")
        
        # 1. Prepare Data
        # Merge signup date into events to calculate "days since signup" for every event at once
        events_merged = self.events_df[['user_id', 'timestamp']].merge(
            cohorts_df[['user_id', 'signup_date', 'cohort']], 
            on='user_id', 
            how='inner'
        )
        
        # Calculate day difference for all 11M rows instantly
        events_merged['days_since_signup'] = (
            events_merged['timestamp'] - events_merged['signup_date']
        ).dt.days
        
        # 2. Build Result DataFrame
        # Start with all users
        retention_df = cohorts_df[['user_id', 'cohort', 'signup_date']].copy()
        
        # 3. Vectorized Check for each Day N
        for day in days:
            # We look for events that happened in the window [day-1, day+1]
            # Get the set of users who were active in this window
            active_users = events_merged[
                (events_merged['days_since_signup'] >= day - 1) & 
                (events_merged['days_since_signup'] <= day + 1)
            ]['user_id'].unique()
            
            # Mark them as True/False efficiently
            retention_df[f'day_{day}_retention'] = retention_df['user_id'].isin(active_users)
        
        print("✅ Calculated Day-N retention")
        return retention_df
        
        # Calculate aggregate retention rates
        summary = {'day': days}
        for day in days:
            summary[f'retention_rate'] = retention_df[f'day_{day}_retention'].mean()
        
        print("✅ Calculated Day-N retention")
        return retention_df


if __name__ == "__main__":
    print("=" * 80)
    print(" COHORT ANALYSIS")
    print("=" * 80)
    print()
    
    # Load data
    users_df = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_profiles.csv')
    events_df = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_events.csv')
    
    # Initialize analyzer
    analyzer = CohortAnalyzer(users_df, events_df)
    
    # Create cohorts
    print("\n--- CREATING COHORTS ---")
    cohorts = analyzer.create_cohorts('monthly')
    print(f"Cohorts: {sorted(cohorts['cohort'].unique())[:5]}...")
    
    # Calculate retention
    print("\n--- CALCULATING RETENTION ---")
    retention = analyzer.calculate_retention(cohorts, 'monthly')
    print(retention.head(20))
    
    # Create retention matrix
    print("\n--- RETENTION MATRIX ---")
    matrix = analyzer.create_retention_matrix(retention)
    print(matrix.head())
    
    # Calculate LTV
    print("\n--- COHORT LTV ---")
    ltv = analyzer.calculate_cohort_ltv(cohorts)
    print(ltv.head())
    
    # Behavior analysis
    print("\n--- COHORT BEHAVIOR ---")
    behavior = analyzer.analyze_cohort_behavior(cohorts)
    print(behavior.head())
    
    # Compare early vs late
    print("\n--- EARLY VS LATE COHORTS ---")
    comparison = analyzer.compare_early_vs_late_cohorts(cohorts, retention)
    
    # Save results
    cohorts.to_csv(PROCESSED_DATA_DIR / 'user_cohorts.csv', index=False)
    retention.to_csv(PROCESSED_DATA_DIR / 'cohort_retention.csv', index=False)
    matrix.to_csv(PROCESSED_DATA_DIR / 'retention_matrix.csv')
    print(f"\n💾 Results saved to {PROCESSED_DATA_DIR}")