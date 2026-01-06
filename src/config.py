"""
Configuration file for Product Analytics Deep-Dive
Author: Ayush Saxena
Date: January 2026
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Directory Paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
DASHBOARDS_DIR = OUTPUT_DIR / "dashboards"
REPORTS_DIR = OUTPUT_DIR / "reports"
SQL_DIR = PROJECT_ROOT / "sql"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SYNTHETIC_DATA_DIR, 
                  FIGURES_DIR, DASHBOARDS_DIR, REPORTS_DIR, SQL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ===== NOTION BUSINESS METRICS (Estimated based on public data) =====
TOTAL_USERS = 30_000_000  # 30M users (2024 estimate)
MONTHLY_ACTIVE_USERS = 10_000_000  # ~33% MAU/Total Users ratio
WEEKLY_ACTIVE_USERS = 7_000_000  # ~70% WAU/MAU ratio
DAILY_ACTIVE_USERS = 3_500_000  # ~35% DAU/MAU ratio

# Revenue metrics (estimated)
TOTAL_PAYING_USERS = 4_000_000  # ~13% conversion to paid
AVERAGE_REVENUE_PER_USER = 96  # $8/month * 12 months
ANNUAL_REVENUE = 400_000_000  # $400M ARR (estimated)

# Growth rates (historical)
USER_GROWTH_RATE_MONTHLY = 0.10  # 10% monthly growth
REVENUE_GROWTH_RATE = 0.15  # 15% monthly revenue growth

# ===== NORTH STAR METRIC =====
# "Weekly Active Collaborative Workspaces"
# Rationale: Measures both engagement and network effects
NORTH_STAR_METRIC = "weekly_active_collaborative_workspaces"
NORTH_STAR_TARGET = 7_500  # Target metric (scaled for 50k user simulation)

# ===== USER FUNNEL STAGES =====
FUNNEL_STAGES = [
    'awareness',          # Visited website/heard about Notion
    'signup',             # Created account
    'activation',         # Created first page
    'engagement',         # Used 3+ times in first week
    'habit_formation',    # Used 3+ weeks in a row
    'collaboration',      # Shared workspace with others
    'monetization'        # Converted to paid plan
]

# Baseline conversion rates (estimated from industry benchmarks)
BASELINE_CONVERSION_RATES = {
    'awareness_to_signup': 0.15,           # 15% signup rate
    'signup_to_activation': 0.60,          # 60% create first page
    'activation_to_engagement': 0.45,      # 45% become engaged users
    'engagement_to_habit': 0.35,           # 35% form habit
    'habit_to_collaboration': 0.50,        # 50% share with others
    'collaboration_to_monetization': 0.25  # 25% convert to paid
}

# ===== COHORT ANALYSIS PARAMETERS =====
COHORT_PERIODS = ['Day 1', 'Day 7', 'Day 14', 'Day 30', 'Day 60', 'Day 90']
RETENTION_DEFINITION = 'returning_user'  # User who logs in again

# ===== GROWTH LEVERS =====
GROWTH_LEVERS = {
    'template_discovery': {
        'description': 'Improve template gallery and recommendations',
        'target_stage': 'activation',
        'expected_lift': 0.08,  # 8% improvement
        'confidence': 'high'
    },
    'viral_sharing': {
        'description': 'Optimize share mechanics and invites',
        'target_stage': 'collaboration',
        'expected_lift': 0.15,  # 15% improvement
        'confidence': 'medium'
    },
    'seo_content': {
        'description': 'Create template and use-case SEO content',
        'target_stage': 'awareness',
        'expected_lift': 0.25,  # 25% improvement
        'confidence': 'high'
    },
    'mobile_experience': {
        'description': 'Improve mobile app engagement',
        'target_stage': 'engagement',
        'expected_lift': 0.12,  # 12% improvement
        'confidence': 'medium'
    },
    'api_integrations': {
        'description': 'Build integrations with popular tools',
        'target_stage': 'habit_formation',
        'expected_lift': 0.10,  # 10% improvement
        'confidence': 'high'
    }
}

# ===== TIME PERIODS =====
ANALYSIS_START_DATE = datetime(2023, 1, 1)
ANALYSIS_END_DATE = datetime(2025, 12, 31)
SIMULATION_DAYS = 365 * 2  # 2 years of data

# ===== USER BEHAVIOR PARAMETERS =====
AVG_PAGES_PER_USER = 15
AVG_SESSIONS_PER_WEEK = 4
AVG_SESSION_DURATION_MINUTES = 12
AVG_COLLABORATORS_PER_WORKSPACE = 3.5

# ===== VISUALIZATION SETTINGS =====
COLOR_SCHEME = {
    'primary': '#2E2E2E',      # Notion black
    'secondary': '#37352F',    # Notion dark gray
    'accent': '#EB5757',       # Notion red
    'success': '#0F7B6C',      # Notion green
    'warning': '#FFA344',      # Notion orange
    'info': '#0B6E99',         # Notion blue
    'background': '#FFFFFF',
    'text': '#37352F'
}

# Chart styling
CHART_STYLE = {
    'font_family': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    'title_size': 18,
    'axis_title_size': 14,
    'label_size': 12,
    'dpi': 300
}

# ===== SQL CONFIGURATION =====
# For demonstration, we'll use pandas but write queries as if for a database
DATABASE_TYPE = 'postgresql'  # What Notion likely uses
SCHEMA_NAME = 'analytics'

print(f"✅ Configuration loaded successfully")
print(f"📁 Project Root: {PROJECT_ROOT}")
print(f"📊 North Star Metric: {NORTH_STAR_METRIC}")
print(f"🎯 Target: {NORTH_STAR_TARGET:,} weekly active collaborative workspaces")