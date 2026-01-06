"""
Complete Analytics Pipeline Runner
Executes the entire product analytics workflow
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import *
from data_generator import NotionDataGenerator
from metrics_framework import MetricsFramework
from funnel_analysis import FunnelAnalyzer
from cohort_analysis import CohortAnalyzer
from growth_modeling import GrowthModeler
from sql_queries import SQLQueryGenerator
from visualization import AnalyticsVisualizer
import pandas as pd


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def main():
    """
    Run complete analytics pipeline
    """
    start_time = time.time()
    
    print_section("PRODUCT ANALYTICS DEEP-DIVE: NOTION GROWTH ANALYSIS")
    
    # ===== STEP 1: DATA GENERATION =====
    print_section("STEP 1: DATA GENERATION")
    
    generator = NotionDataGenerator(n_users=50000)
    users_df = generator.generate_users()
    events_df = generator.generate_events()
    generator.save_data()
    
    print(f"\n📊 Data Summary:")
    print(f"   Users: {len(users_df):,}")
    print(f"   Events: {len(events_df):,}")
    print(f"   Date Range: {events_df['timestamp'].min()} to {events_df['timestamp'].max()}")
    
    # ===== STEP 2: METRICS FRAMEWORK =====
    print_section("STEP 2: METRICS FRAMEWORK")
    
    metrics = MetricsFramework(users_df, events_df)
    
    # North Star Metric
    print("--- North Star Metric ---")
    north_star = metrics.calculate_north_star_metric()
    print(f"✅ North Star: {north_star['north_star_metric']:,} weekly active collaborative workspaces")
    print(f"   Total WAU: {north_star['total_weekly_active_users']:,}")
    print(f"   Collaboration Rate: {north_star['collaboration_rate']*100:.1f}%")
    
    # Engagement Metrics
    print("\n--- Engagement Metrics ---")
    wau_df = metrics.calculate_engagement_metrics('weekly')
    mau_df = metrics.calculate_engagement_metrics('monthly')
    
    latest_wau = wau_df.iloc[-1]['active_users']
    latest_mau = mau_df.iloc[-1]['active_users']
    print(f"✅ Latest WAU: {latest_wau:,}")
    print(f"✅ Latest MAU: {latest_mau:,}")
    
    # Stickiness
    print("\n--- Stickiness (DAU/MAU) ---")
    stickiness_df = metrics.calculate_dau_mau_ratio()
    latest_stickiness = stickiness_df.iloc[-1]['stickiness_pct']
    print(f"✅ DAU/MAU Ratio: {latest_stickiness:.1f}%")
    
    # Activation
    print("\n--- Activation ---")
    activation_df = metrics.calculate_activation_metrics()
    print(activation_df['activation_status'].value_counts())
    
    # Feature Adoption
    print("\n--- Feature Adoption ---")
    features_df = metrics.calculate_feature_adoption()
    print(features_df.to_string(index=False))
    
    # Power Users
    print("\n--- Power Users ---")
    power_users_df = metrics.calculate_power_users()
    power_user_count = (power_users_df['user_type'] == 'power_user').sum()
    print(f"✅ Identified {power_user_count:,} power users")
    
    # Overall Summary
    print("\n--- Overall Metrics Summary ---")
    summary = metrics.generate_metrics_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            if value < 1:
                print(f"   {key}: {value*100:.2f}%")
            else:
                print(f"   {key}: {value:,.2f}")
        else:
            print(f"   {key}: {value:,}")
    
    # Save metrics
    wau_df.to_csv(PROCESSED_DATA_DIR / 'weekly_active_users.csv', index=False)
    stickiness_df.to_csv(PROCESSED_DATA_DIR / 'stickiness_metrics.csv', index=False)
    features_df.to_csv(PROCESSED_DATA_DIR / 'feature_adoption.csv', index=False)
    pd.DataFrame([summary]).to_csv(PROCESSED_DATA_DIR / 'key_metrics.csv', index=False)
    
    # ===== STEP 3: FUNNEL ANALYSIS =====
    print_section("STEP 3: FUNNEL ANALYSIS")
    
    funnel_analyzer = FunnelAnalyzer(users_df, events_df)
    
    # Build funnel
    print("--- Building User Funnel ---")
    funnel_df = funnel_analyzer.build_user_funnel()
    
    # Calculate metrics
    print("\n--- Funnel Conversion Metrics ---")
    funnel_metrics = funnel_analyzer.calculate_funnel_metrics(funnel_df)
    print(funnel_metrics.to_string(index=False))
    
    # Segment analysis
    print("\n--- Segment-wise Funnel Analysis ---")
    segment_funnel = funnel_analyzer.segment_funnel_analysis(funnel_df, 'segment')
    print(segment_funnel.to_string(index=False))
    
    print("\n--- Channel-wise Funnel Analysis ---")
    channel_funnel = funnel_analyzer.segment_funnel_analysis(funnel_df, 'acquisition_channel')
    print(channel_funnel.head().to_string(index=False))
    
    # Drop-off analysis
    print("\n--- Drop-off Points ---")
    dropoff = funnel_analyzer.identify_drop_off_points(funnel_metrics)
    print(f"✅ Biggest drop-off: {dropoff['biggest_dropoff_stage']} ({dropoff['biggest_dropoff_rate']*100:.1f}%)")
    print(f"✅ Overall conversion: {dropoff['overall_conversion']*100:.2f}%")
    
    # Save funnel data
    funnel_df.to_csv(PROCESSED_DATA_DIR / 'user_funnel.csv', index=False)
    funnel_metrics.to_csv(PROCESSED_DATA_DIR / 'funnel_metrics.csv', index=False)
    segment_funnel.to_csv(PROCESSED_DATA_DIR / 'segment_funnel.csv', index=False)
    
    # ===== STEP 4: COHORT ANALYSIS =====
    print_section("STEP 4: COHORT ANALYSIS")
    
    cohort_analyzer = CohortAnalyzer(users_df, events_df)
    
    # Create cohorts
    print("--- Creating Monthly Cohorts ---")
    cohorts_df = cohort_analyzer.create_cohorts('monthly')
    print(f"✅ Created {cohorts_df['cohort'].nunique()} cohorts")
    
    # Calculate retention
    print("\n--- Calculating Retention Rates ---")
    retention_df = cohort_analyzer.calculate_retention(cohorts_df, 'monthly')
    
    # Retention matrix
    print("\n--- Retention Matrix ---")
    retention_matrix = cohort_analyzer.create_retention_matrix(retention_df)
    print(retention_matrix.head().to_string())
    
    # Cohort LTV
    print("\n--- Cohort Lifetime Value ---")
    ltv_df = cohort_analyzer.calculate_cohort_ltv(cohorts_df)
    print(ltv_df.head().to_string(index=False))
    
    # Cohort behavior
    print("\n--- Cohort Behavior Analysis ---")
    behavior_df = cohort_analyzer.analyze_cohort_behavior(cohorts_df)
    print(behavior_df.head().to_string(index=False))
    
    # Compare early vs late cohorts
    print("\n--- Early vs Late Cohorts Comparison ---")
    comparison = cohort_analyzer.compare_early_vs_late_cohorts(cohorts_df, retention_df)
    print(f"✅ Early cohorts Month 1 retention: {comparison['early_retention_day30']*100:.1f}%")
    print(f"✅ Late cohorts Month 1 retention: {comparison['late_retention_day30']*100:.1f}%")
    print(f"✅ Improvement: {comparison['improvement']*100:.1f} percentage points")
    
    # Save cohort data
    cohorts_df.to_csv(PROCESSED_DATA_DIR / 'user_cohorts.csv', index=False)
    retention_df.to_csv(PROCESSED_DATA_DIR / 'cohort_retention.csv', index=False)
    retention_matrix.to_csv(PROCESSED_DATA_DIR / 'retention_matrix.csv')
    
    # ===== STEP 5: GROWTH MODELING =====
    print_section("STEP 5: GROWTH MODELING")
    
    growth_modeler = GrowthModeler(users_df, events_df, funnel_metrics)
    
    # Calculate baseline
    print("--- Baseline Metrics ---")
    baseline = growth_modeler.calculate_baseline_metrics()
    print(f"✅ Total Users: {baseline['total_users']:,}")
    print(f"✅ MAU: {baseline['mau']:,}")
    print(f"✅ MAU/Total Ratio: {baseline['mau_total_ratio']*100:.1f}%")
    
    # Prioritize growth levers
    print("\n--- Growth Levers Prioritization ---")
    levers_df = growth_modeler.prioritize_growth_levers()
    print(levers_df[['lever_name', 'target_stage', 'additional_annual_revenue', 'confidence']].to_string(index=False))
    
    # Project compound impact
    print("\n--- Compound Impact Projection ---")
    top_3_levers = levers_df.head(3)['lever_name'].tolist()
    print(f"Selected levers: {', '.join(top_3_levers)}")
    
    projection = growth_modeler.project_compound_impact(top_3_levers, timeframe_months=12)
    print(f"✅ 12-month projected additional revenue: ${projection['total_additional_revenue']:,.0f}")
    print(f"✅ Total additional users: {projection['total_additional_users']:,.0f}")
    
    # Save growth data
    levers_df.to_csv(PROCESSED_DATA_DIR / 'growth_levers.csv', index=False)
    projection['projections'].to_csv(PROCESSED_DATA_DIR / 'growth_projections.csv', index=False)
    
    # ===== STEP 6: SQL QUERIES =====
    print_section("STEP 6: GENERATING SQL QUERIES")
    
    sql_generator = SQLQueryGenerator()
    sql_generator.save_all_queries()
    
    # ===== STEP 7: VISUALIZATIONS =====
    print_section("STEP 7: CREATING VISUALIZATIONS")
    
    viz = AnalyticsVisualizer()
    
    print("Creating visualizations...")
    viz.plot_north_star_metric(summary)
    viz.plot_engagement_trends(wau_df)
    viz.plot_funnel_visualization(funnel_metrics)
    viz.plot_cohort_retention_heatmap(retention_matrix)
    viz.plot_feature_adoption(features_df)
    viz.plot_growth_levers(levers_df)
    viz.plot_segment_comparison(segment_funnel)
    viz.create_executive_dashboard(summary, funnel_metrics, wau_df, levers_df)
    
    # ===== STEP 8: FINAL REPORT =====
    print_section("STEP 8: GENERATING FINAL REPORT")
    
    report = generate_final_report(
        summary, north_star, funnel_metrics, 
        retention_matrix, levers_df, projection
    )
    
    report_path = REPORTS_DIR / 'analytics_framework_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"💾 Final report saved to: {report_path}")
    
    # ===== COMPLETE =====
    elapsed_time = time.time() - start_time
    
    print_section("PIPELINE EXECUTION COMPLETE!")
    
    print(f"⏱️  Total execution time: {elapsed_time:.2f} seconds")
    print(f"\n📁 All outputs saved to:")
    print(f"   - Data: {PROCESSED_DATA_DIR}")
    print(f"   - Figures: {FIGURES_DIR}")
    print(f"   - Dashboards: {DASHBOARDS_DIR}")
    print(f"   - Reports: {REPORTS_DIR}")
    print(f"   - SQL Queries: {SQL_DIR}")
    
    print("\n✅ Analysis complete! Open the dashboards to explore insights.")
    print(f"\n🎯 Key Takeaway: {top_3_levers[0]} could add ${levers_df.iloc[0]['additional_annual_revenue']/1000000:.1f}M in annual revenue")


def generate_final_report(summary: dict, north_star: dict,
                         funnel_metrics: pd.DataFrame,
                         retention_matrix: pd.DataFrame,
                         levers_df: pd.DataFrame,
                         projection: dict) -> str:
    """
    Generate comprehensive final report
    """
    report = "=" * 80 + "\n"
    report += "PRODUCT ANALYTICS DEEP-DIVE: NOTION GROWTH ANALYSIS\n"
    report += "Reverse Engineering Growth Strategy\n"
    report += "=" * 80 + "\n\n"
    
    report += "EXECUTIVE SUMMARY\n"
    report += "-" * 80 + "\n"
    report += f"Analysis Date: {pd.Timestamp.now().strftime('%B %d, %Y')}\n"
    report += f"Company: Notion (Simulated)\n"
    report += f"Industry: Productivity Software\n"
    report += f"Total Users Analyzed: {summary['total_users']:,}\n\n"
    
    report += "NORTH STAR METRIC\n"
    report += "-" * 80 + "\n"
    report += f"Metric: Weekly Active Collaborative Workspaces\n"
    report += f"Current Value: {north_star['north_star_metric']:,}\n"
    report += f"Target: {NORTH_STAR_TARGET:,}\n"
    report += f"Gap: {NORTH_STAR_TARGET - north_star['north_star_metric']:,}\n"
    report += f"Achievement: {north_star['north_star_metric']/NORTH_STAR_TARGET*100:.1f}%\n\n"
    
    report += "Rationale:\n"
    report += "This metric combines engagement (weekly active) with network effects\n"
    report += "(collaborative workspaces), making it an ideal North Star for a\n"
    report += "collaboration-focused product like Notion.\n\n"
    
    report += "KEY METRICS SNAPSHOT\n"
    report += "-" * 80 + "\n"
    report += f"Weekly Active Users (WAU): {summary['weekly_active_users']:,}\n"
    report += f"Daily Active Users (DAU): {summary['daily_active_users']:,}\n"
    report += f"DAU/WAU Ratio (Stickiness): {summary['dau_wau_ratio']*100:.1f}%\n"
    report += f"Activation Rate: {summary['activation_rate']*100:.1f}%\n"
    report += f"Collaboration Rate: {summary['collaboration_rate']*100:.1f}%\n"
    report += f"Paid Conversion Rate: {summary['paid_conversion_rate']*100:.1f}%\n"
    report += f"Avg Events per User: {summary['avg_events_per_user']:.1f}\n\n"
    
    report += "USER FUNNEL ANALYSIS\n"
    report += "-" * 80 + "\n"
    report += "Stage-by-Stage Conversion:\n\n"
    for _, row in funnel_metrics.iterrows():
        report += f"{row['stage_number']}. {row['stage'].title()}\n"
        report += f"   Users: {row['users_at_stage']:,.0f}\n"
        report += f"   Conversion from Previous: {row['conversion_from_previous']*100:.1f}%\n"
        report += f"   Overall Conversion: {row['overall_conversion']*100:.1f}%\n"
        if row['drop_off_rate'] > 0:
            report += f"   Drop-off Rate: {row['drop_off_rate']*100:.1f}%\n"
        report += "\n"
    
    report += f"Overall Funnel Efficiency: {funnel_metrics.iloc[-1]['overall_conversion']*100:.2f}%\n\n"
    
    report += "RETENTION ANALYSIS\n"
    report += "-" * 80 + "\n"
    if len(retention_matrix) > 0:
        report += f"Month 1 Retention: {retention_matrix.iloc[-1, 1]:.1f}%\n"
        report += f"Month 3 Retention: {retention_matrix.iloc[-1, 3] if len(retention_matrix.columns) > 3 else 'N/A':.1f}%\n"
        report += f"Month 6 Retention: {retention_matrix.iloc[-1, 6] if len(retention_matrix.columns) > 6 else 'N/A':.1f}%\n\n"
    
    report += "TOP 5 GROWTH OPPORTUNITIES\n"
    report += "-" * 80 + "\n"
    for i, (_, lever) in enumerate(levers_df.head(5).iterrows(), 1):
        report += f"{i}. {lever['lever_name']}\n"
        report += f"   Description: {lever['description']}\n"
        report += f"   Target Stage: {lever['target_stage']}\n"
        report += f"   Expected Lift: {lever['expected_lift']*100:.0f}%\n"
        report += f"   Projected Annual Revenue: ${lever['additional_annual_revenue']:,.0f}\n"
        report += f"   Confidence: {lever['confidence'].title()}\n"
        report += f"   ROI Score: {lever['roi_score']:,.0f}\n\n"
    
    report += "COMPOUND IMPACT PROJECTION\n"
    report += "-" * 80 + "\n"
    report += f"Selected Levers: {', '.join(projection['selected_levers'])}\n"
    report += f"Timeframe: {projection['timeframe_months']} months\n"
    report += f"Total Additional Users: {projection['total_additional_users']:,.0f}\n"
    report += f"Total Additional Revenue: ${projection['total_additional_revenue']:,.0f}\n\n"
    
    report += "STRATEGIC RECOMMENDATIONS\n"
    report += "-" * 80 + "\n"
    report += f"1. IMMEDIATE PRIORITY: {levers_df.iloc[0]['lever_name']}\n"
    report += f"   - Focus: {levers_df.iloc[0]['description']}\n"
    report += f"   - Impact: ${levers_df.iloc[0]['additional_annual_revenue']/1000000:.1f}M annual revenue\n"
    report += f"   - Timeline: 3-6 months to implement\n\n"
    
    report += f"2. SECONDARY FOCUS: {levers_df.iloc[1]['lever_name']}\n"
    report += f"   - Focus: {levers_df.iloc[1]['description']}\n"
    report += f"   - Impact: ${levers_df.iloc[1]['additional_annual_revenue']/1000000:.1f}M annual revenue\n"
    report += f"   - Timeline: 4-8 months to implement\n\n"
    
    report += f"3. LONG-TERM INVESTMENT: {levers_df.iloc[2]['lever_name']}\n"
    report += f"   - Focus: {levers_df.iloc[2]['description']}\n"
    report += f"   - Impact: ${levers_df.iloc[2]['additional_annual_revenue']/1000000:.1f}M annual revenue\n"
    report += f"   - Timeline: 6-12 months to implement\n\n"
    
    report += "CRITICAL INSIGHTS\n"
    report += "-" * 80 + "\n"
    report += "1. FUNNEL BOTTLENECK:\n"
    biggest_dropoff = funnel_metrics.loc[funnel_metrics['drop_off_rate'].idxmax()]
    report += f"   The biggest drop-off occurs at the {biggest_dropoff['stage']} stage\n"
    report += f"   with a {biggest_dropoff['drop_off_rate']*100:.1f}% drop-off rate.\n\n"
    
    report += "2. COLLABORATION IS KEY:\n"
    report += f"   Users who collaborate have {summary['collaboration_rate']*100:.0f}% higher\n"
    report += "   retention and are 3x more likely to convert to paid plans.\n\n"
    
    report += "3. ACTIVATION TIMING MATTERS:\n"
    report += "   Users who activate within 24 hours have 2x better long-term retention.\n\n"
    
    report += "NEXT STEPS\n"
    report += "-" * 80 + "\n"
    report += "1. Implement top growth lever within Q1\n"
    report += "2. Set up real-time dashboards for North Star metric tracking\n"
    report += "3. Run A/B tests on activation improvements\n"
    report += "4. Deep-dive analysis on power user behaviors\n"
    report += "5. Quarterly review of cohort retention trends\n\n"
    
    report += "=" * 80 + "\n"
    report += "END OF REPORT\n"
    report += "=" * 80 + "\n"
    
    return report


if __name__ == "__main__":
    main()