"""
Metrics Framework
Defines North Star metric, supporting KPIs, and metric calculation logic
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from config import *


class MetricsFramework:
    """
    Comprehensive metrics framework for product analytics
    """
    
    def __init__(self, users_df: pd.DataFrame, events_df: pd.DataFrame):
        """
        Initialize metrics framework
        
        Args:
            users_df: User profiles DataFrame
            events_df: Events DataFrame
        """
        self.users_df = users_df
        self.events_df = events_df
        
        # Ensure timestamp is datetime
        self.events_df['timestamp'] = pd.to_datetime(self.events_df['timestamp'])
        self.users_df['signup_date'] = pd.to_datetime(self.users_df['signup_date'])
    
    def calculate_north_star_metric(self, date: datetime = None) -> Dict:
        """
        Calculate North Star Metric: Average Weekly Active Collaborative Workspaces (Last 4 Weeks)
        """
        if date is None:
            date = self.events_df['timestamp'].max()
        
        # Look at a 28-day window (4 weeks) to smooth out daily volatility
        start_date = date - timedelta(days=28)
        
        # Filter events for the last 4 weeks
        recent_events = self.events_df[
            (self.events_df['timestamp'] >= start_date) &
            (self.events_df['timestamp'] <= date)
        ].copy()
        
        # Group by week and count unique collaborators per week
        recent_events['week'] = recent_events['timestamp'].dt.to_period('W')
        
        weekly_collaborators = recent_events[
            recent_events['event_type'] == 'workspace_shared'
        ].groupby('week')['user_id'].nunique()
        
        # Calculate the average (Robust North Star)
        if not weekly_collaborators.empty:
            active_collaborative = int(weekly_collaborators.mean())
        else:
            active_collaborative = 0
            
        # Total WAU (average over last 4 weeks)
        weekly_active = recent_events.groupby('week')['user_id'].nunique()
        total_active = int(weekly_active.mean()) if not weekly_active.empty else 0
        
        collaboration_rate = active_collaborative / total_active if total_active > 0 else 0
        
        return {
            'date': date,
            'north_star_metric': active_collaborative,
            'total_weekly_active_users': total_active,
            'collaboration_rate': collaboration_rate,
            'metric_name': NORTH_STAR_METRIC,
            'target': NORTH_STAR_TARGET
        }
    
    def calculate_engagement_metrics(self, period: str = 'weekly') -> pd.DataFrame:
        """
        Calculate engagement metrics (DAU, WAU, MAU)
        
        Args:
            period: Aggregation period ('daily', 'weekly', 'monthly')
            
        Returns:
            DataFrame with engagement metrics over time
        """
        print(f"📊 Calculating {period} engagement metrics...")
        
        # Add date column
        self.events_df['date'] = self.events_df['timestamp'].dt.date
        
        if period == 'daily':
            engagement = self.events_df.groupby('date')['user_id'].nunique().reset_index()
            engagement.columns = ['date', 'active_users']
            engagement['metric_type'] = 'DAU'
        
        elif period == 'weekly':
            self.events_df['week'] = self.events_df['timestamp'].dt.to_period('W')
            engagement = self.events_df.groupby('week')['user_id'].nunique().reset_index()
            engagement.columns = ['period', 'active_users']
            engagement['date'] = engagement['period'].dt.start_time
            engagement['metric_type'] = 'WAU'
            engagement = engagement[['date', 'active_users', 'metric_type']]
        
        else:  # monthly
            self.events_df['month'] = self.events_df['timestamp'].dt.to_period('M')
            engagement = self.events_df.groupby('month')['user_id'].nunique().reset_index()
            engagement.columns = ['period', 'active_users']
            engagement['date'] = engagement['period'].dt.start_time
            engagement['metric_type'] = 'MAU'
            engagement = engagement[['date', 'active_users', 'metric_type']]
        
        # Calculate growth rates
        engagement['growth_rate'] = engagement['active_users'].pct_change()
        
        print(f"✅ Calculated {period} engagement metrics")
        return engagement
    
    def calculate_dau_mau_ratio(self) -> pd.DataFrame:
        """
        Calculate DAU/MAU ratio (stickiness metric) - Optimized for large datasets
        
        Returns:
            DataFrame with stickiness over time
        """
        print("📊 Calculating DAU/MAU ratio (stickiness)...")
        
        # 1. Optimized Data Preparation
        # Instead of scanning the full DF every time, we pre-group users by day.
        # This reduces 11M rows into ~1000 daily buckets.
        daily_activity = self.events_df[['timestamp', 'user_id']].copy()
        daily_activity['date'] = daily_activity['timestamp'].dt.date
        
        # Create a dictionary mapping Date -> Set of User IDs
        # Grouping by day and converting to sets is extremely fast
        daily_users_map = daily_activity.groupby('date')['user_id'].apply(set).to_dict()
        
        # 2. Fast Rolling Calculation
        # We iterate through the date range and just union the sets for the last 30 days.
        min_date = self.events_df['timestamp'].min().date()
        max_date = self.events_df['timestamp'].max().date()
        all_dates = pd.date_range(min_date, max_date)
        
        results = []
        
        for current_timestamp in all_dates:
            current_date = current_timestamp.date()
            
            # DAU: Count of unique users today
            today_users = daily_users_map.get(current_date, set())
            dau = len(today_users)
            
            # MAU: Union of unique users from the last 30 days
            # We look back 30 days and combine their sets
            mau_users = set()
            for i in range(30):
                lookback_date = current_date - timedelta(days=i)
                if lookback_date in daily_users_map:
                    mau_users.update(daily_users_map[lookback_date])
            
            mau = len(mau_users)
            
            # Calculate Ratio
            ratio = dau / mau if mau > 0 else 0
            
            results.append({
                'date': current_timestamp,
                'dau': dau,
                'mau': mau,
                'dau_mau_ratio': ratio,
                'stickiness_pct': ratio * 100
            })
            
        dau_df = pd.DataFrame(results)
        
        print("✅ Calculated DAU/MAU ratio")
        return dau_df[['date', 'dau', 'mau', 'dau_mau_ratio', 'stickiness_pct']]
    
    def calculate_activation_metrics(self) -> pd.DataFrame:
        """
        Calculate activation metrics (time to first value)
        
        Returns:
            DataFrame with activation analysis
        """
        print("📊 Calculating activation metrics...")
        
        # Get first page creation for each user
        first_page = self.events_df[
            self.events_df['event_type'] == 'page_created'
        ].groupby('user_id')['timestamp'].min().reset_index()
        first_page.columns = ['user_id', 'first_page_timestamp']
        
        # Merge with signup dates
        activation = self.users_df[['user_id', 'signup_date']].merge(
            first_page, on='user_id', how='left'
        )
        
        # Calculate time to activation
        activation['time_to_activation_hours'] = (
            activation['first_page_timestamp'] - activation['signup_date']
        ).dt.total_seconds() / 3600
        
        # Classify activation speed
        activation['activation_status'] = 'not_activated'
        activation.loc[
            activation['time_to_activation_hours'] <= 1,
            'activation_status'
        ] = 'fast_activated'
        activation.loc[
            (activation['time_to_activation_hours'] > 1) &
            (activation['time_to_activation_hours'] <= 24),
            'activation_status'
        ] = 'normal_activated'
        activation.loc[
            activation['time_to_activation_hours'] > 24,
            'activation_status'
        ] = 'slow_activated'
        
        # Calculate activation rate
        activation_rate = (
            activation['activation_status'] != 'not_activated'
        ).sum() / len(activation)
        
        print(f"✅ Activation rate: {activation_rate*100:.1f}%")
        return activation
    
    def calculate_feature_adoption(self) -> pd.DataFrame:
        """
        Calculate feature adoption rates
        
        Returns:
            DataFrame with feature usage statistics
        """
        print("📊 Calculating feature adoption...")
        
        # Define key features
        feature_events = {
            'page_creation': 'page_created',
            'content_editing': 'content_edited',
            'search': 'search_performed',
            'collaboration': 'workspace_shared',
            'page_viewing': 'page_viewed'
        }
        
        total_users = self.users_df['user_id'].nunique()
        
        adoption = []
        for feature_name, event_type in feature_events.items():
            users_used = self.events_df[
                self.events_df['event_type'] == event_type
            ]['user_id'].nunique()
            
            adoption_rate = users_used / total_users
            
            # Calculate frequency among users who used it
            usage_frequency = self.events_df[
                self.events_df['event_type'] == event_type
            ].groupby('user_id').size().mean()
            
            adoption.append({
                'feature': feature_name,
                'users_adopted': users_used,
                'adoption_rate': adoption_rate,
                'avg_usage_per_user': usage_frequency
            })
        
        adoption_df = pd.DataFrame(adoption)
        print("✅ Calculated feature adoption")
        return adoption_df
    
    def calculate_power_users(self, top_percentile: float = 0.10) -> pd.DataFrame:
        """
        Identify and analyze power users
        
        Args:
            top_percentile: Top % of users to classify as power users
            
        Returns:
            DataFrame with user segments
        """
        print(f"📊 Identifying power users (top {top_percentile*100:.0f}%)...")
        
        # Calculate user activity levels
        user_activity = self.events_df.groupby('user_id').agg({
            'event_type': 'count',
            'timestamp': ['min', 'max']
        }).reset_index()
        
        user_activity.columns = ['user_id', 'total_events', 'first_activity', 'last_activity']
        
        # Calculate engagement score
        user_activity['days_active'] = (
            user_activity['last_activity'] - user_activity['first_activity']
        ).dt.days + 1
        
        user_activity['events_per_day'] = (
            user_activity['total_events'] / user_activity['days_active']
        )
        
        # Merge with user info
        user_activity = user_activity.merge(
            self.users_df[['user_id', 'segment', 'plan_type']],
            on='user_id'
        )
        
        # Classify users
        threshold = user_activity['events_per_day'].quantile(1 - top_percentile)
        user_activity['user_type'] = 'casual'
        user_activity.loc[
            user_activity['events_per_day'] >= threshold,
            'user_type'
        ] = 'power_user'
        
        print(f"✅ Identified {(user_activity['user_type'] == 'power_user').sum():,} power users")
        return user_activity
    
    def generate_metrics_summary(self) -> Dict:
        """
        Generate comprehensive metrics summary
        
        Returns:
            Dictionary with all key metrics
        """
        print("📊 Generating comprehensive metrics summary...")
        
        # North Star
        north_star = self.calculate_north_star_metric()
        
        # Engagement
        latest_week_events = self.events_df[
            self.events_df['timestamp'] >= (self.events_df['timestamp'].max() - timedelta(days=7))
        ]
        wau = latest_week_events['user_id'].nunique()
        
        latest_day_events = self.events_df[
            self.events_df['timestamp'].dt.date == self.events_df['timestamp'].dt.date.max()
        ]
        dau = latest_day_events['user_id'].nunique()
        
        # Activation
        activated_users = self.events_df[
            self.events_df['event_type'] == 'page_created'
        ]['user_id'].nunique()
        activation_rate = activated_users / len(self.users_df)
        
        # Collaboration
        collaborative_users = self.events_df[
            self.events_df['event_type'] == 'workspace_shared'
        ]['user_id'].nunique()
        collaboration_rate = collaborative_users / activated_users if activated_users > 0 else 0
        
        # Monetization
        paid_users = len(self.users_df[self.users_df['plan_type'] == 'paid'])
        conversion_rate = paid_users / len(self.users_df)
        
        summary = {
            'north_star_metric': north_star['north_star_metric'],
            'total_users': len(self.users_df),
            'weekly_active_users': wau,
            'daily_active_users': dau,
            'dau_wau_ratio': dau / wau if wau > 0 else 0,
            'activation_rate': activation_rate,
            'collaboration_rate': collaboration_rate,
            'paid_conversion_rate': conversion_rate,
            'total_events': len(self.events_df),
            'avg_events_per_user': len(self.events_df) / len(self.users_df)
        }
        
        print("✅ Generated metrics summary")
        return summary


if __name__ == "__main__":
    print("=" * 80)
    print(" METRICS FRAMEWORK")
    print("=" * 80)
    print()
    
    # Load data
    users_df = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_profiles.csv')
    events_df = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_events.csv')
    
    # Initialize framework
    metrics = MetricsFramework(users_df, events_df)
    
    # Calculate metrics
    print("\n--- NORTH STAR METRIC ---")
    north_star = metrics.calculate_north_star_metric()
    print(f"North Star: {north_star['north_star_metric']:,} weekly active collaborative workspaces")
    print(f"Total WAU: {north_star['total_weekly_active_users']:,}")
    print(f"Collaboration Rate: {north_star['collaboration_rate']*100:.1f}%")
    
    print("\n--- ENGAGEMENT METRICS ---")
    wau = metrics.calculate_engagement_metrics('weekly')
    print(wau.tail())
    
    print("\n--- STICKINESS ---")
    stickiness = metrics.calculate_dau_mau_ratio()
    print(f"Latest DAU/MAU: {stickiness['dau_mau_ratio'].iloc[-1]*100:.1f}%")
    
    print("\n--- ACTIVATION ---")
    activation = metrics.calculate_activation_metrics()
    print(activation['activation_status'].value_counts())
    
    print("\n--- FEATURE ADOPTION ---")
    features = metrics.calculate_feature_adoption()
    print(features)
    
    print("\n--- POWER USERS ---")
    power_users = metrics.calculate_power_users()
    print(power_users['user_type'].value_counts())
    
    print("\n--- OVERALL SUMMARY ---")
    summary = metrics.generate_metrics_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            if value < 1:
                print(f"{key}: {value*100:.2f}%")
            else:
                print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value:,}")