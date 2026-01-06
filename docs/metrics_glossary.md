# Metrics Glossary

## North Star Metric

### Weekly Active Collaborative Workspaces
**Definition**: Number of unique workspaces that had at least one collaborative action (shared, invited user, or co-edited) in the past 7 days.

**Why This Metric**:
- Combines engagement (weekly active) with value creation (collaboration)
- Directly correlates with revenue (collaborative users pay more)
- Captures network effects that drive retention
- Actionable: teams can impact it through product changes

**Target**: 5,000,000 workspaces

**Calculation**:
```sql
SELECT COUNT(DISTINCT workspace_id)
FROM events
WHERE event_type IN ('workspace_shared', 'user_invited', 'collaborative_edit')
  AND timestamp >= CURRENT_DATE - INTERVAL '7 days';
```

---

## Engagement Metrics

### DAU (Daily Active Users)
**Definition**: Unique users who performed at least one action in the product on a given day.

**Benchmark**: 
- Good productivity tool: 20-40% of MAU
- Excellent productivity tool: 40-60% of MAU

**Calculation**:
```python
dau = events_df[events_df['date'] == target_date]['user_id'].nunique()
```

### WAU (Weekly Active Users)
**Definition**: Unique users who performed at least one action in the past 7 days.

**Calculation**:
```python
wau = events_df[
    (events_df['date'] >= target_date - timedelta(days=7)) &
    (events_df['date'] <= target_date)
]['user_id'].nunique()
```

### MAU (Monthly Active Users)
**Definition**: Unique users who performed at least one action in the past 30 days.

**Calculation**:
```python
mau = events_df[
    (events_df['date'] >= target_date - timedelta(days=30)) &
    (events_df['date'] <= target_date)
]['user_id'].nunique()
```

### DAU/MAU Ratio (Stickiness)
**Definition**: Percentage of monthly active users who are active daily. Measures product stickiness.

**Benchmark**:
- < 10%: Poor stickiness
- 10-20%: Average
- 20-40%: Good
- 40%+: Excellent (Facebook ~50%, Instagram ~32%)

**Calculation**:
```python
stickiness = (dau / mau) * 100
```

**Interpretation**: A 35% DAU/MAU means the average user is active 10.5 days per month.

---

## Funnel Metrics

### Awareness
**Definition**: Users who have been exposed to the product (visited website, saw ad, heard about it).

**Measurement**: In this analysis, all users represent awareness stage.

### Signup Rate
**Definition**: Percentage of aware users who create an account.

**Benchmark**: 10-20% for freemium products

**Calculation**:
```python
signup_rate = (total_signups / total_awareness) * 100
```

### Activation Rate
**Definition**: Percentage of signed-up users who reach their "aha moment" (first value realization).

**For Notion**: Creating first page/block

**Benchmark**: 40-70% for good onboarding

**Calculation**:
```python
activated_users = users_with_event_type('page_created')
activation_rate = (activated_users / total_signups) * 100
```

### Engagement Rate
**Definition**: Percentage of activated users who use the product regularly (3+ times in first week).

**Benchmark**: 30-50% for productivity tools

**Calculation**:
```python
engaged_users = users_with_3plus_events_in_first_week
engagement_rate = (engaged_users / activated_users) * 100
```

### Collaboration Rate
**Definition**: Percentage of engaged users who share workspaces with others.

**For Notion**: This is critical as it drives retention and monetization

**Benchmark**: 40-60% for collaboration tools

**Calculation**:
```python
collaborative_users = users_with_event_type('workspace_shared')
collaboration_rate = (collaborative_users / engaged_users) * 100
```

### Monetization Rate
**Definition**: Percentage of collaborative users who convert to paid plans.

**Benchmark**: 
- Freemium SaaS: 2-5% overall, 20-40% of power users
- Collaboration tools: 15-30% of teams

**Calculation**:
```python
paid_users = users_with_plan_type('paid')
monetization_rate = (paid_users / collaborative_users) * 100
```

---

## Retention Metrics

### Day-N Retention
**Definition**: Percentage of users from a cohort who return on day N after signup.

**Key Days**: Day 1, 7, 14, 30, 60, 90

**Calculation**:
```python
cohort_users = users_signed_up_on_date
returned_on_day_n = users_active_on_date + timedelta(days=n)
retention = (returned_on_day_n / cohort_users) * 100
```

### Classic Retention
**Definition**: Percentage of users from a cohort who are active in period N.

**Calculation**:
```python
# Month 3 retention
cohort_size = users_signed_up_in_month_0
active_in_month_3 = users_from_cohort_active_in_month_3
retention = (active_in_month_3 / cohort_size) * 100
```

### Rolling Retention
**Definition**: Percentage of users active in period N or any period after N.

**Use Case**: Better for products with irregular usage patterns

---

## Growth Metrics

### User Growth Rate
**Definition**: Month-over-month percentage increase in total users.

**Calculation**:
```python
growth_rate = ((users_this_month - users_last_month) / users_last_month) * 100
```

### Viral Coefficient (K-factor)
**Definition**: Average number of new users each user brings to the product.

**Calculation**:
```python
k_factor = (invites_sent / total_users) * (signups_from_invites / invites_sent)
```

**Benchmark**:
- K > 1: Viral growth
- K = 0.5-1: Strong word-of-mouth
- K < 0.5: Paid acquisition needed

### Quick Ratio
**Definition**: (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)

**Benchmark**:
- < 1: Shrinking
- 1-4: Growing sustainably
- 4+: Hypergrowth

---

## Monetization Metrics

### ARPU (Average Revenue Per User)
**Definition**: Average revenue generated per user (all users, including free).

**Calculation**:
```python
arpu = total_revenue / total_users
```

**For Notion (estimated)**: $3.20/user/month

### ARPPU (Average Revenue Per Paying User)
**Definition**: Average revenue generated per paying user only.

**Calculation**:
```python
arppu = total_revenue / paying_users
```

**For Notion (estimated)**: $8/user/month

### LTV (Lifetime Value)
**Definition**: Total revenue expected from a user over their entire relationship.

**Calculation**:
```python
ltv = arppu * average_lifetime_months
# Or
ltv = arppu * (1 / monthly_churn_rate)
```

**Benchmark**: LTV should be 3x CAC minimum

### CAC (Customer Acquisition Cost)
**Definition**: Average cost to acquire one paying customer.

**Calculation**:
```python
cac = (sales_costs + marketing_costs) / new_customers_acquired
```

### CAC Payback Period
**Definition**: Months required to recover customer acquisition cost.

**Calculation**:
```python
payback_months = cac / (arppu - cogs_per_user)
```

**Benchmark**:
- < 12 months: Excellent
- 12-18 months: Good
- 18-24 months: Acceptable
- 24+ months: Concerning

### Net Revenue Retention (NRR)
**Definition**: Revenue retained from existing customers, including expansions.

**Calculation**:
```python
nrr = ((starting_mrr + expansion - churn - contraction) / starting_mrr) * 100
```

**Benchmark**:
- 100%: Breaking even
- 100-110%: Good
- 110-120%: Great
- 120%+: World-class (best SaaS companies)

---

## Behavioral Metrics

### Time to Activation
**Definition**: Time from signup to first value realization (aha moment).

**Benchmark**: 
- < 5 minutes: Excellent
- 5-30 minutes: Good
- 30-60 minutes: Needs improvement
- 60+ minutes: Poor

**Impact**: Users who activate within 24 hours have 2x better retention.

### Feature Adoption Rate
**Definition**: Percentage of users who have used a specific feature.

**Calculation**:
```python
adoption_rate = (users_who_used_feature / total_active_users) * 100
```

### Feature Depth (Engagement)
**Definition**: Average usage frequency among users who adopted the feature.

**Calculation**:
```python
depth = total_feature_uses / users_who_used_feature
```

### Power User Ratio
**Definition**: Percentage of users in the top engagement tier.

**Calculation**: Top 10% of users by activity level

**Insight**: Power users often drive 50%+ of product usage

---

## Cohort Metrics

### Cohort Size
**Definition**: Number of users who signed up in a specific time period.

### Cohort Retention Curve
**Definition**: Retention rate plotted over time for a specific cohort.

**Shape Analysis**:
- Steep initial drop → Activation problem
- Gradual decline → Engagement problem
- Flattening curve → Found product-market fit

### Cohort LTV
**Definition**: Average lifetime value of users from a specific cohort.

**Use Case**: Compare cohort quality by acquisition channel or time period.

---

## Product Health Metrics

### NPS (Net Promoter Score)
**Definition**: Likelihood users would recommend product (0-10 scale).

**Calculation**:
```python
promoters = responses >= 9
detractors = responses <= 6
nps = (promoters% - detractors%) * 100
```

**Benchmark**:
- < 0: Poor
- 0-30: Good
- 30-70: Great
- 70+: World-class

### CSAT (Customer Satisfaction Score)
**Definition**: Direct satisfaction rating (1-5 or 1-10 scale).

### Active Users / Total Users Ratio
**Definition**: Percentage of all-time users still active.

**Benchmark**:
- < 20%: High churn
- 20-40%: Normal
- 40-60%: Good retention
- 60%+: Excellent

---

## Usage Patterns

### Session Duration
**Definition**: Average time user spends per session.

**For Notion (estimated)**: 12 minutes/session

### Session Frequency
**Definition**: Average sessions per user per week.

**For Notion (estimated)**: 4 sessions/week

### Core Action Frequency
**Definition**: How often users perform the key value action.

**For Notion**: Creating/editing content

---

## Calculation Examples

### Example 1: Calculate DAU/MAU
```python
import pandas as pd

# Given
dau_on_date = 3_500_000
mau_on_date = 10_000_000

# Calculate
stickiness = (dau_on_date / mau_on_date) * 100
# Result: 35%

# Interpretation
days_active_per_month = stickiness / 100 * 30
# Result: 10.5 days/month average
```

### Example 2: Calculate LTV
```python
# Given
arppu = 96  # $8/month * 12 months
average_customer_lifetime_months = 24

# Calculate
ltv = arppu * average_customer_lifetime_months
# Result: $2,304

# Or using churn
monthly_churn_rate = 0.05  # 5% per month
ltv_alternative = arppu / monthly_churn_rate
# Result: $1,920
```

### Example 3: Calculate Funnel Conversion
```python
# Given funnel data
awareness = 1_000_000
signups = 150_000
activated = 90_000
engaged = 40_500
collaborative = 20_250
paid = 5_063

# Calculate stage conversions
signup_rate = (signups / awareness) * 100  # 15%
activation_rate = (activated / signups) * 100  # 60%
engagement_rate = (engaged / activated) * 100  # 45%
collaboration_rate = (collaborative / engaged) * 100  # 50%
monetization_rate = (paid / collaborative) * 100  # 25%

# Overall conversion
overall = (paid / awareness) * 100  # 0.51%
```

---

## References

- **Amplitude**: North Star Framework
- **Mixpanel**: Retention Best Practices
- **Reforge**: Growth Metrics
- **Lenny Rachitsky**: Product-Market Fit Metrics
- **a16z**: Consumer Metrics