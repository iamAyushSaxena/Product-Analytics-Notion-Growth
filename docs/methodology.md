# 📉 Methodology & Analytics Approach

This document outlines the theoretical framework, data generation strategy, and analytical models used in the **Notion Growth Analysis** project. It serves as the reference guide for understanding how metrics are calculated and how growth projections are modeled.

---

## 1. Synthetic Data Strategy (Monte Carlo Simulation)

Since real internal data is not available, this project generates a realistic synthetic dataset using **probabilistic modeling** to simulate user behavior.

### User Generation Model
* **Population Size:** 50,000 unique user profiles.
* **Attributes:** Users are assigned segments (Individual, Small Team, Enterprise) and acquisition channels based on industry-standard probability distributions.
* **Temporal Distribution:** Signups are distributed over a 2-year window using an exponential growth curve to simulate a scaling startup.

### Event Stream Simulation
* **User Journeys:** Each user's actions are simulated day-by-day using Markov Chain-like logic.
* **Engagement Probability:**
    * *Enterprise* users have higher retention and engagement probabilities (0.85) compared to *Individual* users (0.50).
    * *Paid* users have a 1.3x multiplier on engagement probability compared to free users.
* **Event Types:** We simulate realistic events including `page_created`, `content_edited`, `workspace_shared`, and `search_performed`.

---

## 2. North Star Metric Framework

We define the North Star Metric (NSM) as the single metric that best captures the core value delivered to customers.

### Definition
**Metric:** Weekly Active Collaborative Workspaces
* **Why:** Notion's value proposition is not just note-taking (single player) but team collaboration (multi-player).
* **Calculation:** Unique workspaces that had at least one `workspace_shared` or collaborative edit event in the last 7 days.

### Supporting KPIs
* **Engagement:** Weekly Active Users (WAU) and DAU/WAU Ratio (Stickiness).
* **Monetization:** Conversion rate from Free → Paid plan.
* **Retention:** Month-1 and Month-6 retention rates.

---

## 3. Analytical Techniques

### A. Funnel Analysis (The "Pirate" Metrics)
We analyze the user lifecycle using the **AAARRR** framework (Awareness, Acquisition, Activation, Retention, Referral, Revenue).
* **Key Innovation:** We segment the funnel by *User Persona* (e.g., Student vs. Enterprise) to identify specific drop-off points.
* **Time-to-Conversion:** We analyze the velocity of activation (time from `signup` to first `page_created`) to correlate speed with long-term retention.

### B. Cohort Analysis
We group users by their **signup month** to isolate behavioral changes over time.
* **Retention Matrix:** A heat map showing the percentage of users active in Month N after signup.
* **Behavioral Cohorts:** We compare the retention of users who *collaborated* in their first week vs. those who did not, proving the hypothesis that collaboration drives retention.

### C. Growth Modeling
We use a deterministic model to project the impact of specific product interventions ("Growth Levers").
* **Inputs:** Current baseline conversion rates from the funnel analysis.
* **Levers:**
    1.  **Viral Sharing:** Increasing the coefficient of `workspace_shared` events.
    2.  **Template Discovery:** Improving the activation rate by 8%.
* **Compound Impact:** The model calculates the non-linear effect of applying multiple levers simultaneously over a 12-month period using compound growth logic.

---

## 4. Key Assumptions

The following assumptions are used in the revenue and impact calculations (defined in `src/config.py`):

* **Average Revenue Per User (ARPU):** $96/year (Estimated based on standard SaaS pricing).
* **Conversion to Paid:** ~13% baseline conversion rate.
* **User Growth Rate:** 10% month-over-month organic growth.
* **Stickiness Target:** A healthy SaaS product targets a 20%+ DAU/MAU ratio; we benchmark against this.

---

## 5. Tools & Libraries

* **Pandas:** For high-performance data manipulation and aggregation.
* **Plotly:** For interactive, web-ready visualizations.
* **Streamlit:** For building the executive dashboard application.
* **SciPy/Statsmodels:** For statistical validation of observed differences.