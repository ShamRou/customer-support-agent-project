# Machine Learning Features

## Overview

DataPulse uses machine learning to automatically detect data quality issues, predict problems before they occur, and reduce alert fatigue with intelligent anomaly detection.

**Available on**: Pro (ML Anomaly Detection), Enterprise (Full ML Suite)

---

## ML-Powered Anomaly Detection

### What is ML Anomaly Detection?

Instead of setting static thresholds, DataPulse learns normal patterns and alerts when data deviates significantly.

**Traditional Approach** (Static Thresholds):
```yaml
❌ Problems:
- Hard to set right threshold
- Doesn't account for trends
- Misses seasonal patterns
- Many false positives

Volume Monitor:
  Threshold: 90,000 - 110,000 rows
  Issue: Fails every weekend (lower volume)
  Issue: Doesn't catch gradual decline
```

**ML Approach** (Adaptive):
```yaml
✅ Benefits:
- Automatically learns patterns
- Accounts for seasonality
- Adapts to trends
- Reduces false positives

Volume Monitor with ML:
  Method: Auto-detect anomalies
  Sensitivity: Medium
  Training Period: 14 days
  Result: Understands weekday vs weekend patterns
```

---

## How ML Anomaly Detection Works

### 1. Training Phase (14 days)

DataPulse observes your data:
```yaml
Day 1-14: Learning Phase
  - Collect baseline data
  - Identify patterns
  - Detect seasonality (daily, weekly)
  - Calculate normal ranges
  - Build statistical model

Patterns Detected:
  - Weekday average: 100,000 rows
  - Weekend average: 25,000 rows
  - Monday peak: 120,000 rows
  - Friday dip: 85,000 rows
  - Gradual growth: +2% per week
```

### 2. Detection Phase

After training, monitors use ML models:

```yaml
Every Check:
  1. Fetch current metric (e.g., row count)
  2. Compare to ML model prediction
  3. Calculate anomaly score (0-100)
  4. Alert if score > threshold

Anomaly Score:
  - 0-20: Normal variation
  - 21-50: Minor deviation (info)
  - 51-75: Moderate anomaly (warning)
  - 76-100: Severe anomaly (critical)
```

### 3. Continuous Learning

Models adapt over time:
```yaml
Model Updates:
  - Daily: Incorporates yesterday's data
  - Weekly: Re-evaluates patterns
  - Monthly: Full model retrain

Adaptive:
  - Learns new trends
  - Adjusts to business changes
  - Improves accuracy over time
```

---

## ML Features

### 1. Volume Anomaly Detection

**Use Case**: Detect unusual row counts

**Configuration**:
```yaml
Monitor Type: Volume (ML-powered)
Table: orders
Settings:
  Detection Method: Machine Learning
  Sensitivity: Medium
  Training Period: 14 days
  Consider:
    - Day of week patterns
    - Time of day patterns
    - Seasonal trends
    - Growth trends
```

**What It Detects**:
- Sudden drops (data pipeline failure)
- Unexpected spikes (duplicate data)
- Gradual decline (customer churn)
- Missing data (incomplete loads)

**Example Alert**:
```
🚨 Volume Anomaly Detected: orders

Expected: 98,000 ± 12,000 rows (based on Monday pattern)
Actual: 45,000 rows
Anomaly Score: 87/100 (Severe)

Likely Cause: Missing data or pipeline failure
Last 7 Days: 95k, 102k, 97k, 99k, 103k, 28k (Sat), 30k (Sun)
Historical Monday Average: 98,000 rows
```

---

### 2. Distribution Monitoring

**Use Case**: Detect unusual statistical distributions

**Configuration**:
```yaml
Monitor Type: Distribution (ML-powered)
Table: transactions
Column: amount
Settings:
  Track: Mean, Median, P95, P99
  Sensitivity: High
  Alert On: Significant shifts
```

**What It Detects**:
- Pricing errors (mean shifts dramatically)
- Data corruption (sudden outliers)
- Currency issues (amounts in wrong currency)
- Fraud patterns (unusual distribution)

**Example Alert**:
```
🚨 Distribution Anomaly: transactions.amount

Metric: Mean
Expected: $125.50 ± $15.00
Actual: $850.25
Anomaly Score: 95/100

Historical Comparison:
  Last 7 days mean: $120-130
  Last 30 days mean: $118-135
  Today: $850.25 ⚠️

Possible Issues:
  - Pricing error
  - Currency conversion issue
  - Data corruption
```

---

### 3. Freshness Prediction

**Use Case**: Predict when data will become stale

**Configuration**:
```yaml
Monitor Type: Freshness (ML-powered)
Table: user_events
Settings:
  Learn typical update patterns
  Predict next update time
  Alert if prediction missed
```

**What It Does**:
- Learns typical update schedules
- Predicts next expected update
- Alerts proactively if late
- Accounts for variable schedules

**Example Alert**:
```
⚠️ Freshness Prediction Alert: user_events

Prediction: Next update expected at 2:15 AM
Current Time: 2:45 AM
Status: 30 minutes overdue

Confidence: 92%
Based On: Last 60 update cycles
Typical Update Time: 2:10 AM ± 10 min
```

---

### 4. Schema Change Detection (Enterprise)

**Use Case**: Detect unusual schema evolution patterns

**Configuration**:
```yaml
Monitor Type: Schema (ML-powered)
Settings:
  Learn normal schema change frequency
  Detect suspicious patterns
  Predict breaking changes
```

**What It Detects**:
- Unexpected column drops
- Unusual type changes
- Rapid schema churn (instability)
- Non-standard naming patterns

**Example Alert**:
```
⚠️ Unusual Schema Activity: customer_data

Pattern Detected: 5 columns dropped in 24 hours
Normal: 0-1 changes per week
Anomaly Score: 78/100

Recent Changes:
  - phone_number: Dropped
  - email_verified: Dropped
  - last_login: Dropped
  - preferences: Dropped
  - metadata: Dropped

Recommendation: Verify these changes are intentional
Potential Impact: 3 downstream models may break
```

---

### 5. Pattern Learning

**Use Case**: Automatically learn complex patterns

**What It Learns**:
```yaml
Temporal Patterns:
  - Day of week variations
  - Hour of day patterns
  - Weekly seasonality
  - Monthly cycles
  - Holiday impacts

Business Patterns:
  - Marketing campaign effects
  - Product launch impacts
  - Seasonal business cycles
  - Geographic variations

Growth Trends:
  - Linear growth
  - Exponential growth
  - Plateau patterns
  - Decline patterns
```

**Example - E-commerce Orders**:
```
ML Model Learned:
  Monday: 20% higher than average (back to work)
  Friday: 15% lower (end of week)
  Weekends: 70% lower (B2B business)
  First week of month: 30% higher (new budgets)
  December: 3x normal (holiday season)
  Post-campaign: +50% for 3 days

Alerts Only When:
  - Deviation from learned pattern
  - Not explained by known factors
  - Statistically significant
```

---

## Sensitivity Settings

### Low Sensitivity
```yaml
Use When:
  - Exploratory phase
  - High natural variability
  - Tolerate more variance

Characteristics:
  - Fewer alerts
  - Only catch severe issues
  - Lower false positive rate
  - May miss subtle problems
```

### Medium Sensitivity (Recommended)
```yaml
Use When:
  - Production monitoring
  - Balanced approach
  - Most common use case

Characteristics:
  - Moderate alert volume
  - Catches most issues
  - Reasonable false positive rate
  - Good starting point
```

### High Sensitivity
```yaml
Use When:
  - Critical data
  - Low tolerance for issues
  - Early warning preferred

Characteristics:
  - More alerts
  - Catches subtle issues
  - Higher false positive rate
  - Requires more tuning
```

---

## ML vs. Static Thresholds

### Comparison

| Aspect | Static Thresholds | ML-Based |
|--------|------------------|----------|
| **Setup** | Manual configuration | Auto-learns |
| **Accuracy** | Requires tuning | Improves over time |
| **Seasonality** | Manual rules | Automatic |
| **Trends** | Misses gradual changes | Detects trends |
| **Maintenance** | High (manual updates) | Low (auto-adapts) |
| **False Positives** | Often high | Generally lower |
| **Explainability** | Clear rules | Model-based |

### When to Use Each

**Use Static Thresholds When**:
- You have clear, fixed requirements
- Data is very consistent
- Compliance requirements (specific limits)
- Simple pass/fail criteria

**Use ML When**:
- Data has patterns/seasonality
- Volume varies naturally
- Don't know right threshold
- Want to reduce false positives

### Hybrid Approach (Best)
```yaml
Monitor: orders_volume
Checks:
  1. Hard Limit (Static):
     Min: 1,000 rows (absolute minimum)
     Max: 500,000 rows (data integrity check)

  2. Anomaly Detection (ML):
     Expected: ~100,000 rows (varies by day/season)
     Sensitivity: Medium
     Alert if: Anomaly score > 70

Result:
  - Hard limits prevent extreme issues
  - ML catches subtle anomalies
  - Best of both worlds
```

---

## Advanced ML Features (Enterprise Only)

### 1. Predictive Alerting

Predict issues before they happen:

```yaml
Feature: Predictive Alerts
Monitors:
  - Freshness: Predicts data will be stale in 30 min
  - Volume: Detects declining trend (will hit minimum in 2 hours)
  - Distribution: Spots gradual drift (issue likely in 4 hours)

Alert Example:
  "⚠️ Predictive Alert: orders table trending toward staleness
   Current: 45 minutes old (threshold: 1 hour)
   Prediction: Will exceed threshold in 15 minutes at current rate
   Recommendation: Investigate ETL job now to prevent incident"
```

### 2. Root Cause Analysis

ML identifies likely causes:

```yaml
Feature: AI Root Cause Analysis
When Alert Fires:
  1. Analyze historical incidents
  2. Check correlated failures
  3. Review recent changes
  4. Consider time-based factors

Suggested Causes (Ranked):
  1. ETL job failed (80% confidence)
     - Similar pattern in past incidents
     - Job typically runs at this time
     - Downstream impact matches

  2. Source database issue (60% confidence)
     - Multiple tables affected
     - Started at same time
     - Similar to incident 2 weeks ago

  3. Network connectivity (30% confidence)
     - Less likely based on patterns
```

### 3. Auto-Remediation Suggestions

ML recommends fixes:

```yaml
Feature: Smart Recommendations
Alert: Volume anomaly in orders table

AI Recommendations:
  1. Rerun ETL job "daily_orders_pipeline"
     Confidence: 85%
     Based on: 12 past incidents with same pattern
     All resolved by: Job rerun

  2. Check Snowflake warehouse status
     Confidence: 70%
     Based on: 5 past incidents during maintenance windows

  3. Contact: data-eng-oncall@company.com
     Typical resolution time: 45 minutes

One-Click Actions:
  [Rerun Job] [Open Runbook] [Create Incident]
```

### 4. Impact Prediction

Predict downstream effects:

```yaml
Feature: Impact Forecasting
If This Issue Persists:
  In 1 hour:
    - 3 downstream tables will be stale
    - 2 dashboards will show old data
    - ~50 users affected

  In 4 hours:
    - 8 downstream tables affected
    - 5 dashboards broken
    - ~150 users affected
    - Revenue reporting delayed

  In 24 hours:
    - Critical: Executive dashboard outdated
    - Critical: Customer-facing data stale
    - ~500 users affected
```

---

## Best Practices

### 1. Allow Training Period

```yaml
New Monitor:
  Days 1-14: Training mode
    - Collect baseline data
    - Don't alert yet
    - Review patterns

  Day 15+: Active monitoring
    - Start alerting
    - Monitor false positive rate
    - Tune sensitivity if needed
```

### 2. Review ML Insights

```yaml
Weekly Review:
  - Check detected patterns (are they correct?)
  - Review anomaly scores (well calibrated?)
  - Look at false positives (too sensitive?)
  - Adjust sensitivity if needed
```

### 3. Combine with Static Rules

```yaml
Best Practice:
  Static: Absolute boundaries (can't go below 0 rows)
  ML: Normal operation range (detect anomalies)

Example:
  Hard Min: 100 rows (static)
  Hard Max: 1,000,000 rows (static)
  Expected: ~50,000 rows (ML, varies by day/time)
```

### 4. Use Appropriate Sensitivity

```yaml
Critical Production Tables:
  Sensitivity: Medium to High
  Reason: Catch issues early

Dev/Staging Tables:
  Sensitivity: Low to Medium
  Reason: More volatile, less critical

Analytics Tables:
  Sensitivity: Medium
  Reason: Balance coverage and noise
```

---

## Troubleshooting

### Too Many False Positives

**Solution**:
```yaml
1. Lower sensitivity: High → Medium
2. Extend training period: 14 → 30 days
3. Check for data quality issues (garbage in, garbage out)
4. Add business context (exclude known events)
```

### Missing Real Issues

**Solution**:
```yaml
1. Increase sensitivity: Low → Medium
2. Check anomaly score threshold
3. Review what model learned (is baseline correct?)
4. Add static threshold as backup
```

### Model Not Learning Patterns

**Solution**:
```yaml
1. Ensure 14+ days of data
2. Check data consistency
3. Verify sufficient volume
4. Contact support if persists
```

---

## FAQ

**Q: How long until ML is accurate?**
A: 14 days for basic patterns, 30+ days for seasonal patterns

**Q: Does ML replace all static thresholds?**
A: No, combine both. Static for hard limits, ML for operational range.

**Q: What if my data changes dramatically (new product launch)?**
A: Model adapts within 7-14 days. Use "Retrain Model" button for immediate adjustment.

**Q: Can I see what the ML model learned?**
A: Yes, view "ML Insights" tab showing detected patterns and predictions.

**Q: Is ML more expensive?**
A: No, ML is included in Pro and Enterprise plans at no extra cost.

---

## Resources

- ML Feature Documentation: docs.datapulse.io/ml
- Sensitivity Tuning Guide: docs.datapulse.io/ml/tuning
- ML Best Practices: docs.datapulse.io/ml/best-practices
- Support: ml-support@datapulse.io
