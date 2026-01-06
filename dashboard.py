import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Notion Growth Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants for styling
COLOR_PRIMARY = '#2E2E2E'
COLOR_SECONDARY = '#37352F'
COLOR_ACCENT = '#EB5757'
COLOR_SUCCESS = '#0F7B6C'
NORTH_STAR_TARGET = 7500  # Matches your config.py target

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Load all processed data from CSVs"""
    data_path = Path("data/processed")
    
    try:
        data = {
            "wau": pd.read_csv(data_path / "weekly_active_users.csv"),
            "stickiness": pd.read_csv(data_path / "stickiness_metrics.csv"),
            "funnel": pd.read_csv(data_path / "funnel_metrics.csv"),
            "features": pd.read_csv(data_path / "feature_adoption.csv"),
            "retention": pd.read_csv(data_path / "retention_matrix.csv", index_col=0),
            "levers": pd.read_csv(data_path / "growth_levers.csv"),
            "projections": pd.read_csv(data_path / "growth_projections.csv"),
            # NEW: Load the key metrics summary
            "metrics": pd.read_csv(data_path / "key_metrics.csv").iloc[0]
        }
        # Ensure dates are datetime objects
        data["wau"]['date'] = pd.to_datetime(data["wau"]['date'])
        data["stickiness"]['date'] = pd.to_datetime(data["stickiness"]['date'])
        return data
    except FileNotFoundError as e:
        st.error(f"❌ Could not find data files. Please run 'python scripts/run_full_analysis.py' first.\nError: {e}")
        return None

data = load_data()

if not data:
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("📊 Notion Analytics")
    st.markdown("---")
    st.write("Navigation")
    page = st.radio("Go to", ["Executive Summary", "Engagement & Retention", "Growth Modeling"])
    
    st.markdown("---")
    st.info(f"**Data Loaded:**\n{len(data['wau'])} weeks of history")

# --- EXECUTIVE SUMMARY PAGE ---
if page == "Executive Summary":
    st.title("🚀 Executive Growth Dashboard")
    
    # --- NORTH STAR METRIC SECTION (NEW) ---
    st.subheader("🌟 North Star Metric")
    
    ns_col1, ns_col2 = st.columns([1, 2])
    
    with ns_col1:
        st.info(
            """
            **Metric:** Weekly Active Collaborative Workspaces
            
            **Why:** Measures users who are not just active, but *collaborating*.
            This drives network effects and retention.
            """
        )
    
    with ns_col2:
        current_ns_value = data["metrics"]["north_star_metric"]
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_ns_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': NORTH_STAR_TARGET, 'relative': False, 'valueformat': ','},
            gauge={
                'axis': {'range': [None, NORTH_STAR_TARGET * 1.5]},
                'bar': {'color': COLOR_PRIMARY},
                'threshold': {
                    'line': {'color': COLOR_ACCENT, 'width': 4},
                    'thickness': 0.75,
                    'value': NORTH_STAR_TARGET
                },
                'steps': [
                    {'range': [0, NORTH_STAR_TARGET * 0.5], 'color': "#e5e7eb"},
                    {'range': [NORTH_STAR_TARGET * 0.5, NORTH_STAR_TARGET], 'color': "#9ca3af"}
                ]
            }
        ))
        fig_gauge.update_layout(height=350, margin=dict(t=80, b=10, l=30, r=30))
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")
    st.markdown("### High-Level Metrics Snapshot")
    
    # KPI Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    latest_wau = data["wau"].iloc[-1]['active_users']
    wau_growth = (latest_wau - data["wau"].iloc[-2]['active_users']) / data["wau"].iloc[-2]['active_users']
    latest_stickiness = data["stickiness"].iloc[-1]['stickiness_pct']
    activation_rate = data["funnel"][data["funnel"]['stage'] == 'activation']['overall_conversion'].values[0]
    conversion_rate = data["funnel"][data["funnel"]['stage'] == 'monetization']['overall_conversion'].values[0]

    kpi1.metric("Weekly Active Users", f"{latest_wau:,}", f"{wau_growth:.1%}")
    kpi2.metric("Stickiness (DAU/MAU)", f"{latest_stickiness:.1f}%")
    kpi3.metric("Activation Rate", f"{activation_rate*100:.1f}%")
    kpi4.metric("Paid Conversion", f"{conversion_rate*100:.1f}%")
    
    st.markdown("---")
    
    # Row 1: Funnel & Growth Levers
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📍 User Acquisition Funnel")
        fig_funnel = go.Figure(go.Funnel(
            y=data["funnel"]['stage'].str.title(),
            x=data["funnel"]['users_at_stage'],
            textinfo="value+percent initial",
            marker={"color": [COLOR_PRIMARY, COLOR_SECONDARY, '#575757', '#777777', '#999999', '#BBBBBB', '#DDDDDD']}
        ))
        fig_funnel.update_layout(height=400, margin=dict(t=0, b=0))
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with col2:
        st.subheader("🌱 Top Growth Levers (ROI)")
        top_levers = data["levers"].head(5).sort_values("roi_score", ascending=True)
        fig_levers = px.bar(
            top_levers, 
            y="lever_name", 
            x="additional_annual_revenue",
            orientation='h',
            text_auto='.2s',
            color_discrete_sequence=[COLOR_ACCENT],
            labels={"additional_annual_revenue": "Projected Annual Revenue ($)", "lever_name": ""}
        )
        fig_levers.update_layout(height=400, margin=dict(t=0, b=0))
        st.plotly_chart(fig_levers, use_container_width=True)

    # Row 2: Projections
    st.subheader("📈 Revenue Projection (Compound Impact)")
    
    timeframe = st.selectbox(
        "Select Projection Period:",
        options=[12, 6, 3, 1],
        format_func=lambda x: f"{x} Months",
        index=0 
    )
    
    filtered_proj = data["projections"][data["projections"]['month'] <= timeframe]
    
    fig_proj = px.area(
        filtered_proj, 
        x="month", 
        y=["baseline_converted", "improved_converted"],
        labels={"value": "Converted Users", "month": "Months from Now"},
        color_discrete_map={"baseline_converted": "gray", "improved_converted": COLOR_ACCENT}
    )
    
    fig_proj.update_layout(
        title=f"{timeframe}-Month Revenue Projection",
        xaxis=dict(tickmode='linear', dtick=1)
    )
    
    st.plotly_chart(fig_proj, use_container_width=True)

# --- ENGAGEMENT & RETENTION PAGE ---
elif page == "Engagement & Retention":
    st.title("👥 Engagement & Retention Deep Dive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Weekly Active Users (Trend)")
        fig_wau = px.line(data["wau"], x="date", y="active_users", title="WAU Growth")
        fig_wau.update_traces(line_color=COLOR_PRIMARY, fill='tozeroy')
        st.plotly_chart(fig_wau, use_container_width=True)
        
    with col2:
        st.subheader("Stickiness (DAU/MAU)")
        fig_stick = px.line(data["stickiness"], x="date", y="stickiness_pct", title="Stickiness %")
        fig_stick.update_traces(line_color=COLOR_ACCENT)
        st.plotly_chart(fig_stick, use_container_width=True)
        
    st.markdown("---")
    st.subheader("🔥 Cohort Retention Heatmap")
    
    fig_ret = go.Figure(data=go.Heatmap(
        z=data["retention"].values,
        x=data["retention"].columns,
        y=data["retention"].index,
        colorscale='Reds',
        text=data["retention"].values,
        texttemplate='%{text:.1f}%'
    ))
    fig_ret.update_layout(
        xaxis_title="Months Since Signup",
        yaxis_title="Cohort Month",
        height=600
    )
    st.plotly_chart(fig_ret, use_container_width=True)

# --- GROWTH MODELING PAGE ---
elif page == "Growth Modeling":
    st.title("🧪 Growth Modeling & Strategy")
    
    st.subheader("Feature Adoption Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        max_adopt = data["features"]["adoption_rate"].max()
        fig_adopt = px.bar(
            data["features"], 
            x="feature", 
            y="adoption_rate",
            title="Adoption Rate (%)",
            labels={"adoption_rate": "Adoption Rate", "feature": ""},
            text_auto='.1%',
            color_discrete_sequence=[COLOR_PRIMARY]
        )
        fig_adopt.update_traces(textposition='outside', cliponaxis=False)
        fig_adopt.update_layout(yaxis_tickformat=".0%", yaxis=dict(range=[0, max_adopt * 1.2]))
        st.plotly_chart(fig_adopt, use_container_width=True)
        
    with col2:
        max_freq = data["features"]["avg_usage_per_user"].max()
        fig_freq = px.bar(
            data["features"], 
            x="feature", 
            y="avg_usage_per_user",
            title="Usage Frequency (Avg Uses/User)",
            labels={"avg_usage_per_user": "Avg Uses per User", "feature": ""},
            text_auto='.1f',
            color_discrete_sequence=[COLOR_SUCCESS] 
        )
        fig_freq.update_traces(textposition='outside', cliponaxis=False)
        fig_freq.update_layout(yaxis=dict(range=[0, max_freq * 1.2]))
        st.plotly_chart(fig_freq, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Detailed Growth Levers")
    
    levers_display = data["levers"][['lever_name', 'description', 'target_stage', 'expected_lift', 'additional_annual_revenue', 'confidence']].copy()
    levers_display.index = range(1, len(levers_display) + 1)
    st.dataframe(levers_display, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #6b7280; padding: 20px;'>
        <p>📊 <strong>Product Analytics Deep-Dive</strong> - Reverse Engineering Notion's Growth Strategy</p>
        <p>Built with Python, Streamlit, Plotly & Pandas <strong>| Last Updated:</strong> {}</p>
        <p>© 2025 <strong>Ayush Saxena</strong>. All rights reserved.</p>
    </div>
""".format(datetime.now().strftime("%d-%b-%Y At %I:%M %p")), unsafe_allow_html=True)