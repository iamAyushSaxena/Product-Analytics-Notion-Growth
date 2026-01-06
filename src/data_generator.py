"""
Synthetic Data Generator
Creates realistic user behavior data for Notion-like product
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from config import *

np.random.seed(42)  # For reproducibility


class NotionDataGenerator:
    """
    Generates synthetic user behavior data simulating Notion's product
    """
    
    def __init__(self, n_users: int = 50000):
        """
        Initialize data generator
        
        Args:
            n_users: Number of users to generate
        """
        self.n_users = n_users
        self.users_df = None
        self.events_df = None
        
    def generate_users(self) -> pd.DataFrame:
        """
        Generate user profiles with attributes
        
        Returns:
            DataFrame with user profiles
        """
        print(f"📊 Generating {self.n_users:,} user profiles...")
        
        # User IDs
        user_ids = [f"user_{i:06d}" for i in range(self.n_users)]
        
        # Signup dates (distributed over 2 years)
        start_date = ANALYSIS_START_DATE
        end_date = ANALYSIS_END_DATE
        date_range = (end_date - start_date).days
        
        signup_dates = [
            start_date + timedelta(days=int(np.random.exponential(date_range/2)))
            for _ in range(self.n_users)
        ]
        signup_dates = [min(d, end_date) for d in signup_dates]
        
        # User segments
        segments = np.random.choice(
            ['individual', 'small_team', 'enterprise', 'education'],
            size=self.n_users,
            p=[0.45, 0.35, 0.15, 0.05]
        )
        
        # Acquisition channels
        channels = np.random.choice(
            ['organic_search', 'social_media', 'referral', 'paid_ads', 'word_of_mouth', 'content'],
            size=self.n_users,
            p=[0.30, 0.15, 0.25, 0.10, 0.15, 0.05]
        )
        
        # Device types
        devices = np.random.choice(
            ['desktop', 'mobile', 'tablet'],
            size=self.n_users,
            p=[0.65, 0.30, 0.05]
        )
        
        # Geographic regions
        regions = np.random.choice(
            ['North America', 'Europe', 'Asia', 'South America', 'Other'],
            size=self.n_users,
            p=[0.40, 0.30, 0.20, 0.05, 0.05]
        )
        
        # Use case
        use_cases = np.random.choice(
            ['personal_notes', 'project_management', 'documentation', 'knowledge_base', 'crm'],
            size=self.n_users,
            p=[0.35, 0.25, 0.20, 0.15, 0.05]
        )
        
        # Plan type (free vs paid)
        # Higher conversion for teams and enterprise
        plan_types = []
        for segment in segments:
            if segment == 'individual':
                is_paid = np.random.random() < 0.08
            elif segment == 'small_team':
                is_paid = np.random.random() < 0.20
            elif segment == 'enterprise':
                is_paid = np.random.random() < 0.50
            else:  # education
                is_paid = np.random.random() < 0.12
            
            plan_types.append('paid' if is_paid else 'free')
        
        self.users_df = pd.DataFrame({
            'user_id': user_ids,
            'signup_date': signup_dates,
            'segment': segments,
            'acquisition_channel': channels,
            'device_type': devices,
            'region': regions,
            'use_case': use_cases,
            'plan_type': plan_types
        })
        
        print(f"✅ Generated user profiles")
        return self.users_df
    
    def generate_user_journey(self, user_id: str, signup_date: datetime,
                             segment: str, plan_type: str) -> List[Dict]:
        """
        Generate event stream for a single user
        
        Args:
            user_id: User identifier
            signup_date: When user signed up
            segment: User segment
            plan_type: Free or paid
            
        Returns:
            List of event dictionaries
        """
        events = []
        current_date = signup_date
        
        # Determine user engagement level
        if segment == 'enterprise':
            engagement_prob = 0.85
            churn_prob = 0.05
        elif segment == 'small_team':
            engagement_prob = 0.70
            churn_prob = 0.15
        elif segment == 'education':
            engagement_prob = 0.60
            churn_prob = 0.25
        else:  # individual
            engagement_prob = 0.50
            churn_prob = 0.35
        
        # Paid users more engaged
        if plan_type == 'paid':
            engagement_prob *= 1.3
            churn_prob *= 0.5
        
        # Signup event
        events.append({
            'user_id': user_id,
            'event_type': 'signup',
            'timestamp': current_date,
            'properties': {}
        })
        
        # Activation phase (first 7 days)
        activated = False
        for day in range(7):
            current_date = signup_date + timedelta(days=day)
            
            if np.random.random() < engagement_prob:
                # User returns
                n_sessions = np.random.poisson(2) + 1
                
                for session in range(n_sessions):
                    session_time = current_date + timedelta(
                        hours=np.random.uniform(0, 24)
                    )
                    
                    # Page creation
                    if day == 0 or (not activated and np.random.random() < 0.7):
                        n_pages = np.random.poisson(2) + 1
                        for _ in range(n_pages):
                            events.append({
                                'user_id': user_id,
                                'event_type': 'page_created',
                                'timestamp': session_time,
                                'properties': {'page_type': np.random.choice(['note', 'database', 'template'])}
                            })
                        activated = True
                    
                    # Content editing
                    if activated and np.random.random() < 0.8:
                        events.append({
                            'user_id': user_id,
                            'event_type': 'content_edited',
                            'timestamp': session_time,
                            'properties': {'edit_duration': np.random.uniform(2, 30)}
                        })
        
        if not activated:
            # User churned in activation
            return events
        
        # Ongoing usage
        days_since_signup = 7
        max_days = min(365, (ANALYSIS_END_DATE - signup_date).days)
        
        churned = False
        weeks_active = 0
        consecutive_weeks_active = 0
        has_collaborated = False
        
        while days_since_signup < max_days and not churned:
            current_date = signup_date + timedelta(days=days_since_signup)
            
            # Weekly activity check
            week_active = False
            for day_in_week in range(7):
                if days_since_signup + day_in_week >= max_days:
                    break
                
                day_date = current_date + timedelta(days=day_in_week)
                
                if np.random.random() < (engagement_prob * 0.7):  # Slightly lower ongoing engagement
                    week_active = True
                    n_sessions = np.random.poisson(AVG_SESSIONS_PER_WEEK / 7) + 1
                    
                    for _ in range(n_sessions):
                        session_time = day_date + timedelta(hours=np.random.uniform(0, 24))
                        
                        # Various events
                        event_types = ['page_viewed', 'content_edited', 'search_performed']
                        weights = [0.5, 0.3, 0.2]
                        
                        event_type = np.random.choice(event_types, p=weights)
                        events.append({
                            'user_id': user_id,
                            'event_type': event_type,
                            'timestamp': session_time,
                            'properties': {}
                        })
                        
                        # Collaboration events (more likely for teams)
                        if segment in ['small_team', 'enterprise']:
                            # Base probability 15%, increases to 25% if they have done it before (habit loop)
                            collab_prob = 0.25 if has_collaborated else 0.15
                            
                            if np.random.random() < collab_prob:
                                events.append({
                                    'user_id': user_id,
                                    'event_type': 'workspace_shared',
                                    'timestamp': session_time,
                                    'properties': {'collaborators': np.random.randint(1, 8)}
                                })
                                has_collaborated = True
                        
                        # Conversion to paid (for free users)
                        if plan_type == 'free' and has_collaborated:
                            if weeks_active > 4 and np.random.random() < 0.02:
                                events.append({
                                    'user_id': user_id,
                                    'event_type': 'upgraded_to_paid',
                                    'timestamp': session_time,
                                    'properties': {}
                                })
                                plan_type = 'paid'
                                engagement_prob *= 1.2
            
            if week_active:
                weeks_active += 1
                consecutive_weeks_active += 1
            else:
                consecutive_weeks_active = 0
                
                # Churn check
                if np.random.random() < churn_prob:
                    churned = True
            
            days_since_signup += 7
        
        return events
    
    def generate_events(self) -> pd.DataFrame:
        """
        Generate event stream for all users
        
        Returns:
            DataFrame with all events
        """
        if self.users_df is None:
            self.generate_users()
        
        print(f"📊 Generating event stream for {self.n_users:,} users...")
        
        all_events = []
        
        for idx, user in self.users_df.iterrows():
            if idx % 5000 == 0:
                print(f"   Processed {idx:,} users...")
            
            user_events = self.generate_user_journey(
                user['user_id'],
                user['signup_date'],
                user['segment'],
                user['plan_type']
            )
            all_events.extend(user_events)
        
        self.events_df = pd.DataFrame(all_events)
        self.events_df = self.events_df.sort_values('timestamp').reset_index(drop=True)
        
        print(f"✅ Generated {len(self.events_df):,} events")
        return self.events_df
    
    def save_data(self):
        """
        Save generated data to CSV files
        """
        if self.users_df is not None:
            self.users_df.to_csv(SYNTHETIC_DATA_DIR / 'user_profiles.csv', index=False)
            print(f"💾 Saved user profiles to {SYNTHETIC_DATA_DIR / 'user_profiles.csv'}")
        
        if self.events_df is not None:
            self.events_df.to_csv(SYNTHETIC_DATA_DIR / 'user_events.csv', index=False)
            print(f"💾 Saved events to {SYNTHETIC_DATA_DIR / 'user_events.csv'}")


if __name__ == "__main__":
    print("=" * 80)
    print(" NOTION DATA GENERATOR")
    print("=" * 80)
    print()
    
    generator = NotionDataGenerator(n_users=50000)
    
    # Generate users
    users = generator.generate_users()
    print(f"\nUser Distribution:")
    print(users['segment'].value_counts())
    print(f"\nPlan Distribution:")
    print(users['plan_type'].value_counts())
    
    # Generate events
    events = generator.generate_events()
    print(f"\nEvent Distribution:")
    print(events['event_type'].value_counts())
    
    # Save data
    generator.save_data()
    
    print("\n✅ Data generation complete!")