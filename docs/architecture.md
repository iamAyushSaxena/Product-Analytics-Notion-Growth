# System Architecture

## High-Level Architecture
```
┌────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES                             │
│                                                                    │
│         ┌──────────────────┐         ┌───────────────────┐         │
│         │ Synthetic Data   │         │ Business Context  │         │
│         │ Generator        │         │ & Assumptions     │         │
│         │                  │         │                   │         │
│         │ - 50K Users      │         │ - MAU: 10M        │         │
│         │ - 750K Events    │         │ - ARPU: $96       │         │
│         │ - 2 Year Period  │         │ - Growth: 10%     │         │
│         └────────┬─────────┘         └─────────┬─────────┘         │
│                  │                             │                   │
└──────────────────┼─────────────────────────────┼───────────────────┘
                   │                             │
                   ▼                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                        DATA STORAGE LAYER                          │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      CSV Data Files                          │  │
│  │                                                              │  │
│  │          ┌──────────────────┐  ┌──────────────────┐          │  │
│  │          │ user_profiles.csv│  │ user_events.csv  │          │  │
│  │          │                  │  │                  │          │  │
│  │          │ Columns:         │  │ Columns:         │          │  │
│  │          │ - user_id        │  │ - user_id        │          │  │
│  │          │ - signup_date    │  │ - event_type     │          │  │
│  │          │ - segment        │  │ - timestamp      │          │  │
│  │          │ - channel        │  │ - properties     │          │  │
│  │          │ - plan_type      │  │                  │          │  │
│  │          └──────────────────┘  └──────────────────┘          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬──────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────┐
│                     ANALYTICS PROCESSING LAYER                     │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Metrics Framework Module                   │  │
│  │    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  │
│  │    │ North Star   │  │ Engagement   │  │  Activation  │      │  │
│  │    │ Calculation  │  │ Metrics      │  │  Analysis    │      │  │
│  │    │              │  │(DAU/WAU/MAU) │  │              │      │  │
│  │    └──────┬───────┘  └───────┬──────┘  └───────┬──────┘      │  │
│  │           │                  │                 │             │  │
│  └───────────┼──────────────────┼─────────────────┼─────────────┘  │
│              │                  │                 │                │
│  ┌───────────▼──────────────────▼─────────────────▼─────────────┐  │
│  │                  Funnel Analysis Module                      │  │
│  │    ┌──────────────┐  ┌───────────────┐  ┌──────────────┐     │  │
│  │    │ Stage-by-    │  │ Conversion    │  │ Drop-off     │     │  │
│  │    │ Stage        │  │ Rates         │  │ Analysis     │     │  │
│  │    │ Tracking     │  │               │  │              │     │  │
│  │    └──────┬───────┘  └───────┬───────┘  └──────┬───────┘     │  │
│  │           │                  │                 │             │  │
│  └───────────┼──────────────────┼─────────────────┼─────────────┘  │
│              │                  │                 │                │
│  ┌───────────▼──────────────────▼─────────────────▼─────────────┐  │
│  │                   Cohort Analysis Module                     │  │
│  │    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  │
│  │    │ Cohort       │  │ Retention    │  │ LTV          │      │  │
│  │    │ Creation     │  │ Calculation  │  │ Estimation   │      │  │
│  │    │              │  │              │  │              │      │  │
│  │    └──────┬───────┘  └───────┬──────┘  └───────┬──────┘      │  │
│  │           │                  │                 │             │  │
│  └───────────┼──────────────────┼─────────────────┼─────────────┘  │
│              │                  │                 │                │
│  ┌───────────▼──────────────────▼─────────────────▼─────────────┐  │
│  │                  Growth Modeling Module                      │  │
│  │  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐      │  │
│  │  │ Lever         │  │ Impact        │  │ Compound     │      │  │
│  │  │ Identification│  │ Quantification│  │ Projection   │      │  │
│  │  │               │  │               │  │              │      │  │
│  │  └───────────────┘  └───────────────┘  └──────────────┘      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  SQL Query Generator                         │  │
│  │  - Generates production-ready PostgreSQL queries             │  │
│  │  - Templates for all key metrics                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                     VISUALIZATION LAYER                            │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Chart Generation                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │  │
│  │  │ North Star   │  │ Funnel       │  │ Cohort       │        │  │
│  │  │ Gauge        │  │ Visualization│  │ Heatmap      │        │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │  │
│  │  │ Growth       │  │ Segment      │  │ Feature      │        │  │
│  │  │ Levers       │  │ Comparison   │  │ Adoption     │        │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Executive Dashboard Composer                    │  │
│  │  - Combines all visualizations                               │  │
│  │  - Interactive HTML output                                   │  │
│  │  - Plotly-based dynamic charts                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        OUTPUT LAYER                                 │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ Interactive      │  │ Static Charts    │  │ SQL Queries      │   │
│  │     App          │  │      (PNG)       │  │ (.sql files)     │   │
│  │ (Streamlit)      │  │                  │  │                  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ Processed Data   │  │ Executive        │  │ Jupyter          │   │
│  │ (CSV)            │  │ Reports (TXT)    │  │ Notebooks        │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│ START: Run Full Analysis Pipeline                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Data Generation                                         │
│                                                                 │
│ Input:  config.py (parameters)                                  │
│ Process: NotionDataGenerator                                    │
│         ├─ Generate user profiles (50K)                         │
│         ├─ Generate event stream (750K events)                  │
│         └─ Apply realistic behavior patterns                    │
│ Output: user_profiles.csv, user_events.csv                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Metrics Framework                                       │
│                                                                 │
│ Input:  user_profiles.csv, user_events.csv                      │
│ Process: MetricsFramework                                       │
│         ├─ Calculate North Star metric                          │
│         ├─ Compute DAU/WAU/MAU                                  │
│         ├─ Analyze activation patterns                          │
│         ├─ Calculate feature adoption                           │
│         └─ Identify power users                                 │
│ Output: metrics_summary.json, engagement_metrics.csv            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Funnel Analysis                                         │
│                                                                 │
│ Input:  user_profiles.csv, user_events.csv                      │
│ Process: FunnelAnalyzer                                         │
│         ├─ Build 7-stage funnel                                 │
│         ├─ Calculate conversion rates                           │
│         ├─ Segment-wise analysis                                │
│         └─ Identify drop-off points                             │
│ Output: funnel_metrics.csv, segment_funnel.csv                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Cohort Analysis                                         │
│                                                                 │
│ Input:  user_profiles.csv, user_events.csv                      │
│ Process: CohortAnalyzer                                         │
│         ├─ Create monthly cohorts                               │
│         ├─ Calculate retention matrix                           │
│         ├─ Estimate LTV by cohort                               │
│         └─ Compare early vs late cohorts                        │
│ Output: cohort_retention.csv, retention_matrix.csv              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Growth Modeling                                         │
│                                                                 │
│ Input:  All previous outputs + funnel_metrics.csv               │
│ Process: GrowthModeler                                          │
│         ├─ Model 5 growth levers                                │
│         ├─ Calculate revenue impact                             │
│         ├─ Prioritize by ROI                                    │
│         └─ Project compound impact                              │
│ Output: growth_levers.csv, growth_projections.csv               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: SQL Query Generation                                    │
│                                                                 │
│ Input:  Schema configuration                                    │
│ Process: SQLQueryGenerator                                      │
│         ├─ DAU/MAU queries                                      │
│         ├─ Funnel queries                                       │
│         ├─ Cohort queries                                       │
│         └─ Revenue queries                                      │
│ Output: 7 .sql files in sql/ directory                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: Visualization                                           │
│                                                                 │
│ Input:  All processed CSV files                                 │
│ Process: AnalyticsVisualizer                                    │
│         ├─ North Star gauge                                     │
│         ├─ Engagement trends                                    │
│         ├─ Funnel visualization                                 │
│         ├─ Cohort heatmap                                       │
│         ├─ Growth levers chart                                  │
│         └─ Executive dashboard                                  │
│ Output: 8+ HTML dashboards, PNG charts                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: Report Generation                                       │
│                                                                 │
│ Input:  All metrics, analysis results                           │
│ Process: Report Generator                                       │
│         ├─ Executive summary                                    │
│         ├─ Key insights                                         │
│         ├─ Strategic recommendations                            │
│         └─ Next steps                                           │
│ Output: analytics_framework_report.txt                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ END: Complete Analytics Framework                               │
│                                                                 │
│ Deliverables:                                                   │
│ ✓ Synthetic datasets (2 CSV files)                              │
│ ✓ Processed analytics (10+ CSV files)                           │
│ ✓ SQL queries (7 files)                                         │
│ ✓ Interactive dashboards (8+ HTML files)                        │
│ ✓ Executive report (1 TXT file)                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Module Dependencies
```
┌──────────────────┐
│    config.py     │  ← Central configuration
└────────┬─────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         ▼                                         ▼
┌──────────────────┐                    ┌──────────────────┐
│ data_generator.py│                    │ sql_queries.py   │
└────────┬─────────┘                    └──────────────────┘
         │
         │ Generates: user_profiles.csv, user_events.csv
         │
         ├────────────────┬────────────────┬────────────────┐
         │                │                │                │
         ▼                ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│metrics_      │  │funnel_       │  │cohort_       │  │growth_       │
│framework.py  │  │analysis.py   │  │analysis.py   │  │modeling.py   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       │                 │                 │                 │
       └─────────────────┴─────────────────┴─────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ visualization.py │
                        └──────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ Dashboards &     │
                        │ Reports          │
                        └──────────────────┘
```

## Technology Stack
```
┌──────────────────────────────────────────────────────┐
│                  Application Layer                   │
│  ┌────────────────────────────────────────────────┐  │
│  │  run_full_analysis.py (Orchestrator)           │  │
│  │  - Coordinates all modules                     │  │
│  │  - Handles data flow                           │  │
│  │  - Generates final outputs                     │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│                  Business Logic Layer                │
│  ┌────────────────────────────────────────────────┐  │
│  │  Analytics Modules (Python)                    │  │
│  │  - metrics_framework.py                        │  │
│  │  - funnel_analysis.py                          │  │
│  │  - cohort_analysis.py                          │  │
│  │  - growth_modeling.py                          │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│                Data Processing Layer                 │
│  ┌────────────────────────────────────────────────┐  │
│  │  pandas - DataFrame operations                 │  │
│  │  numpy - Numerical computations                │  │
│  │  scipy - Statistical analysis                  │  │
│  │  statsmodels - Time series & regression        │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│               Visualization Layer                    │
│  ┌────────────────────────────────────────────────┐  │
│  │  plotly - Interactive charts                   │  │
│  │  matplotlib - Static visualizations            │  │
│  │  seaborn - Statistical plots                   │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│                  Storage Layer                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  CSV Files (local filesystem)                  │  │
│  │  - Raw data                                    │  │
│  │  - Processed data                              │  │
│  │  - Analysis results                            │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## Performance Characteristics

### Data Volume
- **Users**: 50,000
- **Events**: ~750,000
- **Time Period**: 2 years (730 days)
- **Cohorts**: ~24 monthly cohorts
- **Total Data Size**: ~150 MB

### Processing Time (on standard laptop)
- Data Generation: ~5-10 minutes
- Metrics Calculation: ~30 seconds
- Funnel Analysis: ~45 seconds
- Cohort Analysis: ~60 seconds
- Growth Modeling: ~30 seconds
- Visualization: ~15 seconds
- **Total Runtime**: ~3-5 minutes

### Memory Usage
- Peak Memory: ~2 GB
- Average Memory: ~500 MB
- Recommended RAM: 4 GB+

### Scalability Considerations
- **10x Users (500K)**: ~30 minutes runtime
- **100x Users (5M)**: Consider chunked processing
- **Production Scale**: Move to database (PostgreSQL)

## Integration Points

### For Production Implementation
```
Current (Portfolio)          Production (Real Company)
─────────────────────        ──────────────────────────
CSV Files              →     PostgreSQL/BigQuery
Synthetic Data         →     Real User Events
pandas Processing      →     SQL + pandas
Local Execution        →     Airflow/Scheduled Jobs
Static Reports         →     Real-time Dashboards
Manual Analysis        →     Automated Alerts
```

### API Endpoints (if building a service)
```
GET  /api/v1/metrics/north-star
GET  /api/v1/metrics/engagement?period=weekly
GET  /api/v1/funnel?segment=enterprise
GET  /api/v1/cohorts/retention?period=monthly
GET  /api/v1/growth/levers
POST /api/v1/analysis/run
```

## Security Considerations

### Data Privacy
- All data is synthetic (no PII)
- User IDs are generated (not real)
- Events contain no sensitive information

### For Production
- Encrypt data at rest
- Hash/anonymize user IDs
- Implement RBAC for dashboards
- Audit log all access
- GDPR compliance for EU users

## Deployment Architecture (Production)
```
┌──────────────────────────────────────────────────────┐
│                   Cloud Platform                     │
│                  (AWS/GCP/Azure)                     │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Data Warehouse (BigQuery/Redshift)            │  │
│  │  - user_events table                           │  │
│  │  - user_profiles table                         │  │
│  └──────────────────────┬─────────────────────────┘  │
│                         │                            │
│  ┌──────────────────────▼─────────────────────────┐  │
│  │  Processing Layer (Airflow/dbt)                │  │
│  │  - Daily metrics calculation                   │  │
│  │  - Cohort retention updates                    │  │
│  │  - Funnel analysis refresh                     │  │
│  └──────────────────────┬─────────────────────────┘  │
│                         │                            │
│  ┌──────────────────────▼─────────────────────────┐  │
│  │  Dashboard Layer (Looker/Tableau/Metabase)     │  │
│  │  - Executive dashboards                        │  │
│  │  - Self-service analytics                      │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## Error Handling

### Data Validation
- Check for missing user IDs
- Validate timestamp sequences
- Ensure event types match schema
- Verify cohort calculations

### Graceful Degradation
- Continue pipeline if one module fails
- Log errors to file
- Generate partial reports
- Notify on completion status

## Monitoring & Observability

### Key Metrics to Track
- Pipeline execution time
- Data quality scores
- Dashboard load times
- Query performance
- Error rates

### Alerting Rules
- Pipeline failures
- Data anomalies (sudden drops/spikes)
- North Star metric < threshold
- Retention below benchmarks