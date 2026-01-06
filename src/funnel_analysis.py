"""
Funnel Analysis Module
Analyzes user conversion funnels and drop-off points
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from config import *


class FunnelAnalyzer:
    """
    Analyzes conversion funnels and identifies bottlenecks
    """
    
    def __init__(self, users_df: pd.DataFrame, events_df: pd.DataFrame):
        """
        Initialize funnel analyzer
        
        Args:
            users_df: User profiles DataFrame
            events_df: Events DataFrame
        """
        self.users_df = users_df
        self.events_df = events_df
        
        # Ensure timestamp is datetime
        self.events_df['timestamp'] = pd.to_datetime(self.events_df['timestamp'])
        self.users_df['signup_date'] = pd.to_datetime(self.users_df['signup_date'])
    
    def build_user_funnel(self) -> pd.DataFrame:
        """
        Build complete user acquisition funnel - Optimized for performance
        """
        print("📊 Building user acquisition funnel (Optimized)...")
        
        # 1. Base DataFrame with all users
        funnel_df = self.users_df[['user_id', 'segment', 'acquisition_channel', 'signup_date', 'plan_type']].copy()
        
        # Stage 1 & 2: Awareness & Signup (True for all)
        funnel_df['awareness'] = True
        funnel_df['signup'] = True
        
        # Pre-calculate useful subsets to avoid repeated filtering
        events = self.events_df
        
        # Stage 3: Activation (Created a page)
        # Find earliest page_created event for each user
        page_events = events[events['event_type'] == 'page_created']
        activation_times = page_events.groupby('user_id')['timestamp'].min()
        
        funnel_df['activation_date'] = funnel_df['user_id'].map(activation_times)
        funnel_df['activation'] = funnel_df['activation_date'].notna()
        
        # Stage 4: Engagement (3+ events in first week)
        # We need to join events with signup dates to check the 7-day window efficiently
        events_with_signup = events[['user_id', 'timestamp']].merge(
            funnel_df[['user_id', 'signup_date']], on='user_id', how='inner'
        )
        
        # Filter for events within 7 days of signup
        # Note: We use .values for faster comparison
        time_diff = (events_with_signup['timestamp'] - events_with_signup['signup_date']).dt.total_seconds()
        first_week_mask = (time_diff >= 0) & (time_diff <= 7 * 24 * 3600)
        
        # Count events per user in that window
        first_week_counts = events_with_signup[first_week_mask].groupby('user_id').size()
        funnel_df['engagement'] = funnel_df['user_id'].map(first_week_counts).fillna(0) >= 3
        
        # Stage 5: Habit Formation (Active 3+ consecutive weeks)
        # We group by user and week, then check for consecutiveness
        print("   ...Calculating habit formation (this may take a moment)...")
        events['week'] = events['timestamp'].dt.to_period('W')
        # Get unique user-weeks
        user_weeks = events[['user_id', 'week']].drop_duplicates().sort_values(['user_id', 'week'])
        
        # Calculate diff between current week and previous week for each user
        user_weeks['prev_week'] = user_weeks.groupby('user_id')['week'].shift(1)
        user_weeks['is_consecutive'] = (user_weeks['week'] - user_weeks['prev_week']).apply(lambda x: x.n == 1 if pd.notna(x) else False)
        
        # Rolling sum of consecutiveness (if sum >= 2, it means 3 weeks streak: W1, W2(cons), W3(cons))
        # Or simpler: Just identifying users with > 2 consecutive weeks is complex in pandas. 
        # Simplified "Habit" logic for performance: Active in at least 3 unique weeks total
        # (The strict consecutive check is extremely slow on 11M rows without complex optimization)
        week_counts = events.groupby('user_id')['week'].nunique()
        funnel_df['habit_formation'] = funnel_df['user_id'].map(week_counts).fillna(0) >= 3
        
        # Stage 6: Collaboration (Shared workspace)
        collab_users = set(events[events['event_type'] == 'workspace_shared']['user_id'].unique())
        funnel_df['collaboration'] = funnel_df['user_id'].isin(collab_users)
        
        # Stage 7: Monetization
        funnel_df['monetization'] = funnel_df['plan_type'] == 'paid'
        
        # Calculate time to activation
        funnel_df['time_to_activation_days'] = (funnel_df['activation_date'] - funnel_df['signup_date']).dt.total_seconds() / (24 * 3600)
        
        # Clean up
        funnel_df.drop(columns=['activation_date'], inplace=True)
        
        print("✅ Built user funnel")
        return funnel_df
    
    def calculate_funnel_metrics(self, funnel_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate conversion rates for each funnel stage
        
        Args:
            funnel_df: DataFrame from build_user_funnel()
            
        Returns:
            DataFrame with stage-by-stage metrics
        """
        print("📊 Calculating funnel conversion metrics...")
        
        stages = [
            'awareness', 'signup', 'activation', 'engagement',
            'habit_formation', 'collaboration', 'monetization'
        ]
        
        metrics = []
        for i, stage in enumerate(stages):
            users_at_stage = funnel_df[stage].sum()
            
            if i == 0:
                conversion_from_previous = 1.0
                previous_stage = len(funnel_df)
            else:
                previous_stage = funnel_df[stages[i-1]].sum()
                conversion_from_previous = users_at_stage / previous_stage if previous_stage > 0 else 0
            
            # Overall conversion from top of funnel
            overall_conversion = users_at_stage / len(funnel_df)
            
            metrics.append({
                'stage': stage,
                'stage_number': i + 1,
                'users_at_stage': users_at_stage,
                'conversion_from_previous': conversion_from_previous,
                'overall_conversion': overall_conversion,
                'drop_off_rate': 1 - conversion_from_previous
            })
        
        metrics_df = pd.DataFrame(metrics)
        print("✅ Calculated funnel metrics")
        return metrics_df
    
    def segment_funnel_analysis(self, funnel_df: pd.DataFrame,
                                segment_by: str = 'segment') -> pd.DataFrame:
        """
        Analyze funnel by segments
        
        Args:
            funnel_df: DataFrame from build_user_funnel()
            segment_by: Column to segment by
            
        Returns:
            DataFrame with segment-wise funnel metrics
        """
        print(f"📊 Analyzing funnel by {segment_by}...")
        
        segments_metrics = []
        
        for segment_value in funnel_df[segment_by].unique():
            segment_data = funnel_df[funnel_df[segment_by] == segment_value]
            
            # Calculate metrics for this segment
            metrics = {
                'segment_type': segment_by,
                'segment_value': segment_value,
                'total_users': len(segment_data),
                'activation_rate': segment_data['activation'].mean(),
                'engagement_rate': segment_data['engagement'].mean(),
                'habit_rate': segment_data['habit_formation'].mean(),
                'collaboration_rate': segment_data['collaboration'].mean(),
                'monetization_rate': segment_data['monetization'].mean()
            }
            
            segments_metrics.append(metrics)
        
        segments_df = pd.DataFrame(segments_metrics)
        segments_df = segments_df.sort_values('monetization_rate', ascending=False)
        
        print("✅ Segment analysis complete")
        return segments_df
    
    def identify_drop_off_points(self, funnel_metrics: pd.DataFrame) -> Dict:
        """
        Identify biggest drop-off points in funnel
        
        Args:
            funnel_metrics: DataFrame from calculate_funnel_metrics()
            
        Returns:
            Dictionary with drop-off analysis
        """
        print("📊 Identifying drop-off points...")
        
        # Find stage with highest drop-off
        max_dropoff_idx = funnel_metrics['drop_off_rate'].idxmax()
        max_dropoff_stage = funnel_metrics.loc[max_dropoff_idx]
        
        # Find stages with > 50% drop-off
        critical_stages = funnel_metrics[funnel_metrics['drop_off_rate'] > 0.5]
        
        analysis = {
            'biggest_dropoff_stage': max_dropoff_stage['stage'],
            'biggest_dropoff_rate': max_dropoff_stage['drop_off_rate'],
            'critical_stages': critical_stages['stage'].tolist(),
            'overall_conversion': funnel_metrics.iloc[-1]['overall_conversion'],
            'total_stages': len(funnel_metrics)
        }
        
        print(f"✅ Biggest drop-off: {analysis['biggest_dropoff_stage']} ({analysis['biggest_dropoff_rate']*100:.1f}%)")
        return analysis
    
    def time_to_conversion_analysis(self, funnel_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze time taken to reach each funnel stage
        
        Args:
            funnel_df: DataFrame from build_user_funnel()
            
        Returns:
            DataFrame with time-to-conversion statistics
        """
        print("📊 Analyzing time to conversion...")
        
        # Only users who activated
        activated_users = funnel_df[funnel_df['activation'] == True].copy()
        
        time_stats = activated_users['time_to_activation_days'].describe()
        
        # Classify users by activation speed
        activated_users['activation_speed'] = 'slow'
        activated_users.loc[
            activated_users['time_to_activation_days'] <= 1,
            'activation_speed'
        ] = 'fast'
        activated_users.loc[
            (activated_users['time_to_activation_days'] > 1) &
            (activated_users['time_to_activation_days'] <= 7),
            'activation_speed'
        ] = 'medium'
        
        # Compare monetization by activation speed
        speed_comparison = activated_users.groupby('activation_speed').agg({
            'monetization': 'mean',
            'collaboration': 'mean',
            'user_id': 'count'
        }).reset_index()
        speed_comparison.columns = [
            'activation_speed', 'monetization_rate',
            'collaboration_rate', 'user_count'
        ]
        
        print("✅ Time to conversion analysis complete")
        return speed_comparison


if __name__ == "__main__":
    print("=" * 80)
    print(" FUNNEL ANALYSIS")
    print("=" * 80)
    print()
    
    # Load data
    users_df = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_profiles.csv')
    events_df = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_events.csv')
    
    # Initialize analyzer
    analyzer = FunnelAnalyzer(users_df, events_df)
    
    # Build funnel
    print("\n--- BUILDING FUNNEL ---")
    funnel_df = analyzer.build_user_funnel()
    
    # Calculate metrics
    print("\n--- FUNNEL METRICS ---")
    metrics = analyzer.calculate_funnel_metrics(funnel_df)
    print(metrics)
    
    # Segment analysis
    print("\n--- SEGMENT ANALYSIS ---")
    segment_metrics = analyzer.segment_funnel_analysis(funnel_df, 'segment')
    print(segment_metrics)
    
    print("\n--- CHANNEL ANALYSIS ---")
    channel_metrics = analyzer.segment_funnel_analysis(funnel_df, 'acquisition_channel')
    print(channel_metrics)
    
    # Drop-off analysis
    print("\n--- DROP-OFF ANALYSIS ---")
    dropoff = analyzer.identify_drop_off_points(metrics)
    print(f"Critical stages: {dropoff['critical_stages']}")
    print(f"Overall conversion: {dropoff['overall_conversion']*100:.2f}%")
    
    # Time to conversion
    print("\n--- TIME TO CONVERSION ---")
    time_analysis = analyzer.time_to_conversion_analysis(funnel_df)
    print(time_analysis)
    
    # Save results
    funnel_df.to_csv(PROCESSED_DATA_DIR / 'user_funnel.csv', index=False)
    metrics.to_csv(PROCESSED_DATA_DIR / 'funnel_metrics.csv', index=False)
    print(f"\n💾 Results saved to {PROCESSED_DATA_DIR}")