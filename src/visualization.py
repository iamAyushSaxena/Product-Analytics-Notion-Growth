"""
Visualization Module
Creates beautiful, interactive dashboards and charts
"""

from os import name
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List
from config import *

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = CHART_STYLE['font_family']
plt.rcParams['font.size'] = CHART_STYLE['label_size']


class AnalyticsVisualizer:
    """
    Creates visualizations for product analytics
    """
    
    def __init__(self):
        self.colors = COLOR_SCHEME
    
    def plot_north_star_metric(self, metrics_summary: Dict) -> None:
        """
        Create North Star metric visualization
        
        Args:
            metrics_summary: Dictionary with metrics
        """
        fig = go.Figure()
        
        # North Star gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=metrics_summary['north_star_metric'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Weekly Active Collaborative Workspaces<br>(North Star Metric)"},
            delta={'reference': NORTH_STAR_TARGET, 'valueformat': ','},
            gauge={
                'axis': {'range': [None, NORTH_STAR_TARGET * 1.2]},
                'bar': {'color': self.colors['primary']},
                'steps': [
                    {'range': [0, NORTH_STAR_TARGET * 0.5], 'color': "lightgray"},
                    {'range': [NORTH_STAR_TARGET * 0.5, NORTH_STAR_TARGET * 0.8], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': NORTH_STAR_TARGET
                }
            }
        ))
        
        fig.update_layout(
            height=500,
            font={'size': 16, 'family': CHART_STYLE['font_family']}
        )
        
        fig.write_html(FIGURES_DIR / 'north_star_metric.html')
        print("✅ Saved: north_star_metric.html")
    
    def plot_engagement_trends(self, engagement_df: pd.DataFrame) -> None:
        """
        Create engagement trends visualization (DAU, WAU, MAU)
        
        Args:
            engagement_df: DataFrame with engagement metrics
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=engagement_df['date'],
            y=engagement_df['active_users'],
            mode='lines',
            name=engagement_df['metric_type'].iloc[0],
            line=dict(color=self.colors['primary'], width=3),
            fill='tozeroy',
            fillcolor='rgba(46, 46, 46, 0.1)'
        ))
        
        fig.update_layout(
            title="User Engagement Trend",
            xaxis_title="Date",
            yaxis_title="Active Users",
            hovermode='x unified',
            height=500,
            font={'family': CHART_STYLE['font_family']}
        )
        
        fig.write_html(FIGURES_DIR / 'engagement_trends.html')
        print("✅ Saved: engagement_trends.html")
    
    def plot_funnel_visualization(self, funnel_metrics: pd.DataFrame) -> None:
        """
        Create interactive funnel visualization
        
        Args:
            funnel_metrics: DataFrame with funnel metrics
        """
        fig = go.Figure()
        
        fig.add_trace(go.Funnel(
            name='User Funnel',
            y=funnel_metrics['stage'],
            x=funnel_metrics['users_at_stage'],
            textinfo="value+percent initial",
            marker=dict(
                color=[self.colors['primary'], self.colors['secondary'],
                       self.colors['success'], self.colors['info'],
                       self.colors['warning'], self.colors['accent'],
                       self.colors['primary']]
            )
        ))
        
        fig.update_layout(
            title="User Acquisition Funnel",
            height=600,
            font={'family': CHART_STYLE['font_family'], 'size': 14}
        )
        
        fig.write_html(FIGURES_DIR / 'user_funnel.html')
        print("✅ Saved: user_funnel.html")
    
    def plot_cohort_retention_heatmap(self, retention_matrix: pd.DataFrame) -> None:
        """
        Create retention cohort heatmap
        
        Args:
            retention_matrix: Retention matrix from cohort analysis
        """
        fig = go.Figure(data=go.Heatmap(
            z=retention_matrix.values,
            x=[f"Month {i}" for i in retention_matrix.columns],
            y=[str(idx)[:7] for idx in retention_matrix.index],
            colorscale=[
                [0, '#fee5d9'],
                [0.25, '#fcae91'],
                [0.5, '#fb6a4a'],
                [0.75, '#de2d26'],
                [1, '#a50f15']
            ],
            text=retention_matrix.values,
            texttemplate='%{text:.1f}%',
            textfont={"size": 10},
            colorbar=dict(title="Retention %")
        ))
        
        fig.update_layout(
            title="Cohort Retention Heatmap",
            xaxis_title="Months Since Signup",
            yaxis_title="Signup Cohort",
            height=800,
            font={'family': CHART_STYLE['font_family']}
        )
        
        fig.write_html(FIGURES_DIR / 'cohort_retention_heatmap.html')
        print("✅ Saved: cohort_retention_heatmap.html")
    
    def plot_feature_adoption(self, adoption_df: pd.DataFrame) -> None:
        """
        Create feature adoption visualization
        
        Args:
            adoption_df: DataFrame with feature adoption metrics
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Adoption Rate', 'Usage Frequency'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Adoption rate
        fig.add_trace(
            go.Bar(
                x=adoption_df['feature'],
                y=adoption_df['adoption_rate'] * 100,
                marker_color=self.colors['primary'],
                text=adoption_df['adoption_rate'].apply(lambda x: f"{x*100:.1f}%"),
                textposition='outside',
                name='Adoption Rate'
            ),
            row=1, col=1
        )
        
        # Usage frequency
        fig.add_trace(
            go.Bar(
                x=adoption_df['feature'],
                y=adoption_df['avg_usage_per_user'],
                marker_color=self.colors['success'],
                text=adoption_df['avg_usage_per_user'].apply(lambda x: f"{x:.1f}"),
                textposition='outside',
                name='Avg Uses'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="Feature Adoption Analysis",
            showlegend=False,
            height=500,
            font={'family': CHART_STYLE['font_family']}
        )
        
        fig.update_yaxes(title_text="Adoption Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="Avg Uses per User", row=1, col=2)
        
        fig.write_html(FIGURES_DIR / 'feature_adoption.html')
        print("✅ Saved: feature_adoption.html")
    
    def plot_growth_levers(self, levers_df: pd.DataFrame) -> None:
        """
        Create growth levers prioritization visualization
        
        Args:
            levers_df: DataFrame with growth lever impact
        """
        fig = go.Figure()
        
        # Sort by ROI score
        levers_df = levers_df.sort_values('roi_score', ascending=True)
        
        # Color by confidence
        colors_map = {'high': self.colors['success'], 
                     'medium': self.colors['warning'],
                     'low': self.colors['accent']}
        bar_colors = [colors_map[c] for c in levers_df['confidence']]
        
        fig.add_trace(go.Bar(
            y=levers_df['lever_name'],
            x=levers_df['additional_annual_revenue'] / 1000000,  # In millions
            orientation='h',
            marker_color=bar_colors,
            text=levers_df['additional_annual_revenue'].apply(lambda x: f"${x/1000000:.1f}M"),
            textposition='outside',
            hovertemplate=(
                '<b>%{y}</b><br>' +
                'Revenue Impact: $%{x:.2f}M<br>' +
                '<extra></extra>'
            )
        ))
        
        fig.update_layout(
            title="Growth Levers: Projected Annual Revenue Impact",
            xaxis_title="Additional Annual Revenue ($M)",
            yaxis_title="",
            height=600,
            font={'family': CHART_STYLE['font_family']},
            showlegend=False
        )
        
        fig.write_html(FIGURES_DIR / 'growth_levers.html')
        print("✅ Saved: growth_levers.html")
    
    def plot_segment_comparison(self, segment_metrics: pd.DataFrame) -> None:
        """
        Create segment comparison visualization
        
        Args:
            segment_metrics: DataFrame with segment-wise metrics
        """
        fig = go.Figure()
        
        metrics = ['activation_rate', 'engagement_rate', 'collaboration_rate', 'monetization_rate']
        
        for metric in metrics:
            fig.add_trace(go.Bar(
                x=segment_metrics['segment_value'],
                y=segment_metrics[metric] * 100,
                name=metric.replace('_', ' ').title(),
                text=segment_metrics[metric].apply(lambda x: f"{x*100:.1f}%"),
                textposition='outside'
            ))
        
        fig.update_layout(
            title="Conversion Rates by Segment",
            xaxis_title="User Segment",
            yaxis_title="Conversion Rate (%)",
            barmode='group',
            height=600,
            font={'family': CHART_STYLE['font_family']},
            hovermode='x unified'
        )
        
        fig.write_html(FIGURES_DIR / 'segment_comparison.html')
        print("✅ Saved: segment_comparison.html")
    
    def create_executive_dashboard(self, metrics_summary: Dict,
                                   funnel_metrics: pd.DataFrame,
                                   engagement_df: pd.DataFrame,
                                   levers_df: pd.DataFrame) -> None:
        """
        Create comprehensive executive dashboard
        
        Args:
            metrics_summary: Dictionary with key metrics
            funnel_metrics: Funnel metrics DataFrame
            engagement_df: Engagement metrics DataFrame
            levers_df: Growth levers DataFrame
        """
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'North Star Metric',
                'Key Metrics Summary',
                'User Funnel',
                'Engagement Trend',
                'Top Growth Opportunities',
                'Segment Performance'
            ),
            specs=[
                [{'type': 'indicator'}, {'type': 'table'}],
                [{'type': 'funnel'}, {'type': 'scatter'}],
                [{'type': 'bar'}, {'type': 'bar'}]
            ],
            row_heights=[0.25, 0.4, 0.35]
        )
        
        # 1. North Star Metric
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=metrics_summary['north_star_metric'],
                delta={'reference': NORTH_STAR_TARGET, 'relative': True, 'valueformat': '.1%'},
                title={'text': "Weekly Active<br>Collaborative Workspaces"},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=1
        )
        
        # 2. Key Metrics Table
        metrics_data = [
            ['Total Users', f"{metrics_summary['total_users']:,}"],
            ['Weekly Active Users', f"{metrics_summary['weekly_active_users']:,}"],
            ['Daily Active Users', f"{metrics_summary['daily_active_users']:,}"],
            ['DAU/WAU Ratio', f"{metrics_summary['dau_wau_ratio']*100:.1f}%"],
            ['Activation Rate', f"{metrics_summary['activation_rate']*100:.1f}%"],
            ['Paid Conversion', f"{metrics_summary['paid_conversion_rate']*100:.1f}%"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'],
                           fill_color=self.colors['primary'],
                           font=dict(color='white', size=12),
                           align='left'),
                cells=dict(values=list(zip(*metrics_data)),
                          fill_color='white',
                          align='left',
                          font=dict(size=11))
            ),
            row=1, col=2
        )
        
        # 3. User Funnel
        fig.add_trace(
            go.Funnel(
                y=funnel_metrics['stage'][:5],  # Top 5 stages
                x=funnel_metrics['users_at_stage'][:5],
                textinfo="value+percent initial",
                marker=dict(color=self.colors['primary'])
            ),
            row=2, col=1
        )
        
        # 4. Engagement Trend (last 30 days)
        recent_engagement = engagement_df.tail(30)
        fig.add_trace(
            go.Scatter(
                x=recent_engagement['date'],
                y=recent_engagement['active_users'],
                mode='lines',
                line=dict(color=self.colors['success'], width=2),
                fill='tozeroy',
                name='Active Users'
            ),
            row=2, col=2
        )
        
        # 5. Top Growth Opportunities
        top_levers = levers_df.head(5).sort_values('roi_score', ascending=True)
        fig.add_trace(
            go.Bar(
                y=top_levers['lever_name'],
                x=top_levers['additional_annual_revenue'] / 1000000,
                orientation='h',
                marker_color=self.colors['accent'],
                text=top_levers['additional_annual_revenue'].apply(lambda x: f"${x/1000000:.1f}M"),
                textposition='outside'
            ),
            row=3, col=1
        )

        # 6. Placeholder for segment performance (would need actual data)
        fig.add_trace(
            go.Bar(
                x=['Individual', 'Small Team', 'Enterprise', 'Education'],
                y=[8, 20, 50, 12],
                marker_color=self.colors['info'],
                text=['8%', '20%', '50%', '12%'],
                textposition='outside'
            ),
            row=3, col=2
        )
            
        fig.update_layout(
            height=1600,
            showlegend=False,
            title_text="Product Analytics Executive Dashboard - Notion Growth Analysis",
            title_font_size=20,
            title_x=0.5,
            font={'family': CHART_STYLE['font_family']}
        )
            
        fig.update_xaxes(title_text="Users", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=2)
        fig.update_yaxes(title_text="Active Users", row=2, col=2)
        fig.update_xaxes(title_text="Revenue Impact ($M)", row=3, col=1)
        fig.update_yaxes(title_text="", row=3, col=1)
        fig.update_yaxes(title_text="Conversion Rate (%)", row=3, col=2)
            
        fig.write_html(DASHBOARDS_DIR / 'executive_dashboard.html')
        print("✅ Saved: executive_dashboard.html")
        

if name == "main":
    print("=" * 80)
    print(" ANALYTICS VISUALIZATION")
    print("=" * 80)
    print()

    # This would load actual processed data
    # For demonstration, we'll show the structure
    
    print("Visualization module ready.")
    print("Run the full pipeline to generate all visualizations.")