"""
Growth Modeling Module
Quantifies impact of growth levers and projects future growth
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from config import *


class GrowthModeler:
    """
    Models growth levers and projects impact
    """
    
    def __init__(self, users_df: pd.DataFrame, events_df: pd.DataFrame,
                 funnel_metrics: pd.DataFrame):
        """
        Initialize growth modeler
        
        Args:
            users_df: User profiles DataFrame
            events_df: Events DataFrame
            funnel_metrics: Funnel metrics from FunnelAnalyzer
        """
        self.users_df = users_df
        self.events_df = events_df
        self.funnel_metrics = funnel_metrics
    
    def calculate_baseline_metrics(self) -> Dict:
        """
        Calculate current baseline metrics
        
        Returns:
            Dictionary with baseline metrics
        """
        print("📊 Calculating baseline metrics...")
        
        total_users = len(self.users_df)
        mau = self.events_df[
            self.events_df['timestamp'] >= (
                self.events_df['timestamp'].max() - timedelta(days=30)
            )
        ]['user_id'].nunique()
        
        baseline = {
            'total_users': total_users,
            'mau': mau,
            'mau_total_ratio': mau / total_users if total_users > 0 else 0,
            'avg_events_per_user': len(self.events_df) / total_users
        }
        
        # Add funnel stage metrics
        for _, row in self.funnel_metrics.iterrows():
            baseline[f"{row['stage']}_rate"] = row['conversion_from_previous']
        
        print("✅ Baseline metrics calculated")
        return baseline
    
    def model_growth_lever_impact(self, lever_name: str,
                                  lever_config: Dict) -> Dict:
        """
        Model impact of a specific growth lever
        
        Args:
            lever_name: Name of the growth lever
            lever_config: Configuration from GROWTH_LEVERS
            
        Returns:
            Dictionary with impact projections
        """
        print(f"📊 Modeling impact of: {lever_name}...")
        
        baseline = self.calculate_baseline_metrics()
        target_stage = lever_config['target_stage']
        expected_lift = lever_config['expected_lift']
        
        # Get current conversion rate for target stage
        current_rate = baseline.get(f"{target_stage}_rate", 0)
        improved_rate = current_rate * (1 + expected_lift)
        
        # Calculate downstream impact
        # Find position of target stage in funnel
        funnel_stages = self.funnel_metrics['stage'].tolist()
        target_idx = funnel_stages.index(target_stage) if target_stage in funnel_stages else -1
        
        if target_idx == -1:
            print(f"⚠️ Stage {target_stage} not found in funnel")
            return {}
        
        # Calculate users at each stage with improvement
        users_at_stages = {}
        total_users = baseline['total_users']
        
        for i, stage in enumerate(funnel_stages):
            if i == 0:
                users_at_stages[stage] = total_users
            else:
                prev_stage = funnel_stages[i-1]
                stage_rate = baseline.get(f"{stage}_rate", 0)
                
                # Apply improvement if this is the target stage
                if stage == target_stage:
                    stage_rate = improved_rate
                
                users_at_stages[stage] = users_at_stages[prev_stage] * stage_rate
        
        # Calculate baseline users at final stage
        baseline_final_users = users_at_stages[funnel_stages[0]]
        for i in range(1, len(funnel_stages)):
            baseline_final_users *= baseline.get(f"{funnel_stages[i]}_rate", 0)
        
        # Additional users from improvement
        additional_users = users_at_stages[funnel_stages[-1]] - baseline_final_users
        
        # Revenue impact (assuming conversion to paid)
        additional_revenue_annual = additional_users * AVERAGE_REVENUE_PER_USER * 0.13  # 13% conversion
        
        impact = {
            'lever_name': lever_name,
            'target_stage': target_stage,
            'expected_lift': expected_lift,
            'current_rate': current_rate,
            'improved_rate': improved_rate,
            'additional_users_at_target': (
                users_at_stages[target_stage] - total_users * current_rate
            ),
            'additional_final_users': additional_users,
            'additional_annual_revenue': additional_revenue_annual,
            'confidence': lever_config['confidence']
        }
        
        print(f"✅ Projected additional revenue: ${additional_revenue_annual:,.0f}")
        return impact
    
    def prioritize_growth_levers(self) -> pd.DataFrame:
        """
        Model all growth levers and prioritize by impact
        
        Returns:
            DataFrame with all levers ranked by impact
        """
        print("📊 Modeling all growth levers...")
        
        lever_impacts = []
        
        for lever_name, lever_config in GROWTH_LEVERS.items():
            impact = self.model_growth_lever_impact(lever_name, lever_config)
            if impact:
                impact['description'] = lever_config['description']
                lever_impacts.append(impact)
        
        levers_df = pd.DataFrame(lever_impacts)
        levers_df = levers_df.sort_values('additional_annual_revenue', ascending=False)
        
        # Add ROI score (simplified)
        # Higher confidence and lower effort = higher ROI
        confidence_weights = {'high': 1.0, 'medium': 0.7, 'low': 0.4}
        levers_df['confidence_weight'] = levers_df['confidence'].map(confidence_weights)
        levers_df['roi_score'] = (
            levers_df['additional_annual_revenue'] * levers_df['confidence_weight']
        )
        
        levers_df = levers_df.sort_values('roi_score', ascending=False)
        
        print("✅ Growth levers prioritized")
        return levers_df
    
    def project_compound_impact(self, selected_levers: List[str],
                               timeframe_months: int = 12) -> Dict:
        """
        Project compound impact of multiple levers over time
        
        Args:
            selected_levers: List of lever names to apply
            timeframe_months: Projection timeframe
            
        Returns:
            Dictionary with projection results
        """
        print(f"📊 Projecting compound impact over {timeframe_months} months...")
        
        baseline = self.calculate_baseline_metrics()
        current_users = baseline['total_users']
        current_mau = baseline['mau']
        
        # Apply improvements to funnel
        improved_rates = {}
        for stage in self.funnel_metrics['stage'].tolist():
            improved_rates[stage] = baseline.get(f"{stage}_rate", 0)
        
        # Apply each selected lever
        for lever_name in selected_levers:
            if lever_name in GROWTH_LEVERS:
                lever_config = GROWTH_LEVERS[lever_name]
                target_stage = lever_config['target_stage']
                expected_lift = lever_config['expected_lift']
                
                if target_stage in improved_rates:
                    improved_rates[target_stage] *= (1 + expected_lift)
        
        # Project growth month by month
        projections = []
        
        for month in range(timeframe_months + 1):
            # Organic growth
            organic_growth_factor = (1 + USER_GROWTH_RATE_MONTHLY) ** month
            projected_users = current_users * organic_growth_factor
            
            # Calculate users through improved funnel
            funnel_users = projected_users
            for stage in self.funnel_metrics['stage'].tolist()[1:]:  # Skip awareness
                funnel_users *= improved_rates.get(stage, 0)
            
            # Calculate baseline funnel for comparison
            baseline_funnel_users = projected_users
            for stage in self.funnel_metrics['stage'].tolist()[1:]:
                baseline_funnel_users *= baseline.get(f"{stage}_rate", 0)
            
            additional_converted = funnel_users - baseline_funnel_users
            
            projections.append({
                'month': month,
                'total_users': projected_users,
                'baseline_converted': baseline_funnel_users,
                'improved_converted': funnel_users,
                'additional_converted': additional_converted,
                'lift_pct': (additional_converted / baseline_funnel_users * 100) if baseline_funnel_users > 0 else 0
            })
        
        projections_df = pd.DataFrame(projections)
        
        # Calculate cumulative impact
        total_additional_users = projections_df['additional_converted'].sum()
        total_additional_revenue = total_additional_users * AVERAGE_REVENUE_PER_USER * 0.13
        
        result = {
            'selected_levers': selected_levers,
            'timeframe_months': timeframe_months,
            'total_additional_users': total_additional_users,
            'total_additional_revenue': total_additional_revenue,
            'projections': projections_df
        }
        
        print(f"✅ Projected additional revenue: ${total_additional_revenue:,.0f}")
        return result
    
    def sensitivity_analysis(self, lever_name: str,
                            lift_range: Tuple[float, float] = (0.05, 0.30)) -> pd.DataFrame:
        """
        Perform sensitivity analysis on a growth lever
        
        Args:
            lever_name: Name of the lever to analyze
            lift_range: Range of lifts to test (min, max)
            
        Returns:
            DataFrame with sensitivity results
        """
        print(f"📊 Performing sensitivity analysis for: {lever_name}...")
        
        if lever_name not in GROWTH_LEVERS:
            print(f"⚠️ Lever {lever_name} not found")
            return pd.DataFrame()
        
        lever_config = GROWTH_LEVERS[lever_name].copy()
        
        # Test different lift values
        lift_values = np.linspace(lift_range[0], lift_range[1], 10)
        
        results = []
        for lift in lift_values:
            lever_config['expected_lift'] = lift
            impact = self.model_growth_lever_impact(lever_name, lever_config)
            
            results.append({
                'lift_pct': lift * 100,
                'additional_revenue': impact['additional_annual_revenue'],
                'additional_users': impact['additional_final_users']
            })
        
        sensitivity_df = pd.DataFrame(results)
        
        print("✅ Sensitivity analysis complete")
        return sensitivity_df


if __name__ == "__main__":
    print("=" * 80)
    print(" GROWTH MODELING")
    print("=" * 80)
    print()
    
    # Load data
    users_df = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_profiles.csv')
    events_df = pd.read_csv(SYNTHETIC_DATA_DIR / 'user_events.csv')
    funnel_metrics = pd.read_csv(PROCESSED_DATA_DIR / 'funnel_metrics.csv')
    
    # Initialize modeler
    modeler = GrowthModeler(users_df, events_df, funnel_metrics)
    
    # Calculate baseline
    print("\n--- BASELINE METRICS ---")
    baseline = modeler.calculate_baseline_metrics()
    for key, value in baseline.items():
        if isinstance(value, float) and value < 1:
            print(f"{key}: {value*100:.2f}%")
        else:
            print(f"{key}: {value:,.0f}")
    
    # Prioritize growth levers
    print("\n--- GROWTH LEVERS PRIORITIZATION ---")
    levers = modeler.prioritize_growth_levers()
    print(levers[['lever_name', 'additional_annual_revenue', 'confidence', 'roi_score']])
    
    # Project compound impact
    print("\n--- COMPOUND IMPACT PROJECTION ---")
    top_3_levers = levers.head(3)['lever_name'].tolist()
    projection = modeler.project_compound_impact(top_3_levers, timeframe_months=12)
    print(f"Selected levers: {projection['selected_levers']}")
    print(f"12-month projected revenue: ${projection['total_additional_revenue']:,.0f}")
    print(projection['projections'].tail())
    
    # Sensitivity analysis
    print("\n--- SENSITIVITY ANALYSIS ---")
    sensitivity = modeler.sensitivity_analysis(levers.iloc[0]['lever_name'])
    print(sensitivity)
    
    # Save results
    levers.to_csv(PROCESSED_DATA_DIR / 'growth_levers.csv', index=False)
    projection['projections'].to_csv(PROCESSED_DATA_DIR / 'growth_projections.csv', index=False)
    print(f"\n💾 Results saved to {PROCESSED_DATA_DIR}")