# Lab Logbook - Product Analytics Deep-Dive

## Step-by-Step Execution Workflow

### Prerequisites (10 minutes)
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed from requirements.txt
- [ ] Project structure verified

---

## Phase 1: Data Generation (30 minutes)

### Objective
Generate realistic synthetic data simulating 50,000 Notion users over 2 years.

### Steps
1. **Configure parameters** in `src/config.py`:
   - Set user count: 50,000
   - Date range: Jan 2023 - Dec 2025
   - Business metrics (MAU, revenue, etc.)

2. **Run data generator**:
```cmd
   python src/data_generator.py
```

3. **Verify outputs**:
   - Check `data/synthetic/user_profiles.csv` (50,000 rows)
   - Check `data/synthetic/user_events.csv` (~500,000-1M events)

4. **Review data quality**:
   - User segments distributed correctly
   - Event types realistic
   - Timestamps sequential

### Expected Results
- 50,000 user profiles
- ~750,000 events
- 4 user segments (individual, small_team, enterprise, education)
- 6 acquisition channels
- ~13% paid conversion rate

### Time: 5-10 minutes runtime

---

## Phase 2: Metrics Framework (45 minutes)

### Objective
Calculate North Star metric and all supporting KPIs.

### Steps
1. **Define North Star Metric**:
   - Rationale: Weekly Active Collaborative Workspaces
   - Combines engagement (weekly active) + network effects (collaboration)

2. **Calculate engagement metrics**:
```cmd
   python src/metrics_framework.py
```

3. **Review outputs**:
   - North Star: ~2.1M collaborative workspaces
   - WAU: ~7M users
   - MAU: ~10M users
   - DAU/MAU ratio: ~35%
   - Activation rate: ~60%

4. **Document insights**:
   - Stickiness benchmark (DAU/MAU > 30% is good for productivity tools)
   - Activation rate comparison (60% is above industry average)
   - Feature adoption rates

### Key Metrics Calculated
- Daily Active Users (DAU)
- Weekly Active Users (WAU)
- Monthly Active Users (MAU)
- DAU/MAU Ratio (Stickiness)
- Activation Rate
- Feature Adoption Rates
- Power User Segmentation

### Time: 2-3 minutes runtime

---

## Phase 3: Funnel Analysis (60 minutes)

### Objective
Build and analyze 7-stage user acquisition funnel.

### Steps
1. **Define funnel stages**:
   - Awareness → Signup → Activation → Engagement → Habit → Collaboration → Monetization

2. **Run funnel analysis**:
```cmd
   python src/funnel_analysis.py
```

3. **Analyze conversions**:
   - Stage-by-stage conversion rates
   - Identify biggest drop-offs
   - Segment-wise performance

4. **Compare segments**:
   - Enterprise vs Individual users
   - Channel performance (referral vs paid ads)
   - Activation speed impact on retention

### Key Findings
- Overall funnel conversion: ~1.2% (signup to paid)
- Biggest drop-off: Activation → Engagement (55% drop)
- Enterprise users convert 6x better than individuals
- Fast activators (< 24 hours) have 2x better retention

### Deliverables
- `funnel_metrics.csv`
- `segment_funnel.csv`
- Drop-off analysis report

### Time: 30-45 seconds runtime

---

## Phase 4: Cohort Analysis (60 minutes)

### Objective
Analyze user retention by signup cohort over time.

### Steps
1. **Create monthly cohorts**:
   - Group users by signup month
   - Track activity in subsequent months

2. **Run cohort analysis**:
```cmd
   python src/cohort_analysis.py
```

3. **Calculate retention rates**:
   - Day 1, 7, 14, 30, 60, 90 retention
   - Month-over-month retention curves
   - Cohort LTV estimates

4. **Compare early vs late cohorts**:
   - Product improvements reflected in retention
   - Late cohorts show 8% better Month 1 retention

### Key Insights
- Month 1 retention: 45%
- Month 3 retention: 29%
- Month 6 retention: 19%
- Power law: 10% of users drive 50% of activity

### Deliverables
- `cohort_retention.csv`
- `retention_matrix.csv` (heatmap data)
- LTV by cohort analysis

### Time: 30-45 seconds runtime

---

## Phase 5: Growth Modeling (90 minutes)

### Objective
Identify and quantify 5 major growth opportunities.

### Steps
1. **Define growth levers**:
   - Template discovery improvement
   - Viral sharing optimization
   - SEO content strategy
   - Mobile experience enhancement
   - API/integrations expansion

2. **Model each lever**:
```cmd
   python src/growth_modeling.py
```

3. **Calculate impact**:
   - Revenue projections
   - User acquisition estimates
   - Confidence levels

4. **Prioritize by ROI**:
   - Rank by revenue impact × confidence
   - Create implementation timeline

5. **Project compound impact**:
   - Select top 3 levers
   - Model 12-month projection
   - Calculate cumulative revenue

### Key Results
- #1 Lever: SEO Content → $12.5M annual revenue
- #2 Lever: Viral Sharing → $7.8M annual revenue
- #3 Lever: Templates → $6.2M annual revenue
- Compound 12-month impact: $26.5M additional revenue

### Deliverables
- `growth_levers.csv`
- `growth_projections.csv`
- Sensitivity analysis charts

### Time: 1-2 minutes runtime

---

## Phase 6: SQL Queries (30 minutes)

### Objective
Generate production-ready SQL queries for all key metrics.

### Steps
1. **Generate query templates**:
```cmd
   python src/sql_queries.py
```

2. **Review queries for**:
   - DAU/MAU metrics
   - Funnel analysis
   - Cohort retention
   - Power users
   - Feature adoption
   - Revenue metrics
   - North Star metric

3. **Customize for your database**:
   - Adjust schema names
   - Optimize indexes
   - Add filters as needed

### Deliverables
- 7 SQL files in `sql/` directory
- Ready to run on PostgreSQL
- Documented and commented

### Time: < 1 second runtime

---

## Phase 7: Visualizations (45 minutes)

### Objective
Create beautiful, interactive dashboards.

### Steps
1. **Generate all visualizations**:
   - Included in main pipeline
   - Or run individually:
```cmd
   python src/visualization.py
```

2. **Review outputs**:
   - North Star metric gauge
   - Engagement trends
   - Funnel visualization
   - Cohort retention heatmap
   - Feature adoption charts
   - Growth levers bar chart
   - Executive dashboard

3. **Open dashboards**:
```cmd
   start outputs\dashboards\executive_dashboard.html
```

### Deliverables
- 8+ interactive HTML visualizations
- Executive dashboard (comprehensive)
- Print-ready PNG charts

### Time: 10-15 seconds runtime

---

## Phase 8: Final Report (30 minutes)

### Objective
Generate executive summary and recommendations.

### Steps
1. **Run complete pipeline**:
```cmd
   python scripts\run_full_analysis.py
```

2. **Review generated report**:
   - Open `outputs/reports/analytics_framework_report.txt`

3. **Customize recommendations**:
   - Add company-specific context
   - Adjust timelines
   - Include stakeholder notes

### Report Sections
- Executive Summary
- North Star Metric Analysis
- Key Metrics Snapshot
- Funnel Analysis
- Retention Insights
- Growth Opportunities (ranked)
- Strategic Recommendations
- Next Steps

### Time: Full pipeline ~3-5 minutes

---

## Quality Checks

### Data Quality
- [ ] No missing user IDs
- [ ] Timestamps sequential
- [ ] Conversion rates realistic (1-20%)
- [ ] Event distributions make sense

### Analysis Quality
- [ ] Metrics calculated correctly
- [ ] Funnel stages flow logically
- [ ] Retention curves show decay
- [ ] Growth projections reasonable

### Visualization Quality
- [ ] All charts render correctly
- [ ] Colors consistent with brand
- [ ] Labels clear and readable
- [ ] Interactive elements work

### Documentation Quality
- [ ] All code commented
- [ ] README complete
- [ ] SQL queries documented
- [ ] Report clear and actionable

---

## Total Timeline

| Phase | Time | Cumulative |
|-------|------|------------|
| 1. Data Generation | 30 min | 30 min |
| 2. Metrics Framework | 45 min | 1h 15min |
| 3. Funnel Analysis | 60 min | 2h 15min |
| 4. Cohort Analysis | 60 min | 3h 15min |
| 5. Growth Modeling | 90 min | 4h 45min |
| 6. SQL Queries | 30 min | 5h 15min |
| 7. Visualizations | 45 min | 6h |
| 8. Final Report | 30 min | 6h 30min |

**Total: ~6.5 hours** (spread over 2-3 days for thorough analysis)

**Actual Runtime: ~5 minutes** (for code execution)

---

## Key Learnings

### Technical Learnings
1. Synthetic data generation at scale
2. Complex funnel analysis with segments
3. Cohort retention mathematics
4. Growth modeling with confidence intervals
5. SQL optimization for analytics

### Product Learnings
1. North Star metrics must combine engagement + value
2. Activation is the most critical stage
3. Collaboration drives retention and monetization
4. Early product improvements compound over time
5. Data-driven prioritization beats intuition

### Communication Learnings
1. Visualizations must tell a story
2. Executive dashboards need context
3. Recommendations must be actionable
4. Quantify everything (revenue, users, time)
5. Present ranges, not point estimates

---

## Common Issues & Solutions

**Issue**: Data generation takes too long
- **Solution**: Reduce `n_users` parameter to 10,000-25,000

**Issue**: Memory error during analysis
- **Solution**: Process data in chunks, use `chunksize` parameter

**Issue**: Visualizations don't render
- **Solution**: Install kaleido: `pip install kaleido`

**Issue**: SQL queries don't match your database
- **Solution**: Adjust schema names in `config.py`

---

## Next Steps

After completing this project:
1. Adapt framework for your product
2. Connect to real data sources
3. Set up automated reporting
4. Build real-time dashboards
5. Implement top growth levers
6. Track impact and iterate

---

## Resources

- [Amplitude Product Analytics Guide](https://amplitude.com/north-star)
- [Mixpanel Cohort Analysis](https://mixpanel.com/blog/cohort-analysis/)
- [Lenny's Newsletter - Growth](https://www.lennysnewsletter.com/)
- [Reforge Growth Series](https://www.reforge.com/)