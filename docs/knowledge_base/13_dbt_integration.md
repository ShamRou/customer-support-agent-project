# dbt Integration Guide

## Overview

DataPulse integrates seamlessly with dbt (data build tool) to automatically create monitors from your dbt tests, track model freshness, and maintain data quality throughout your transformation pipeline.

**Available on**: Pro and Enterprise plans

---

## Why Integrate dbt with DataPulse?

### Benefits

1. **Automatic Monitor Creation**: dbt tests → DataPulse monitors
2. **Enhanced Visibility**: See dbt model lineage in DataPulse
3. **Production Monitoring**: Continuous monitoring beyond dbt test runs
4. **Unified Dashboard**: Data quality metrics across all sources
5. **Better Alerting**: Advanced routing and notification options
6. **Historical Tracking**: Long-term data quality trends

---

## Integration Methods

### Method 1: dbt Cloud (Recommended)

**Best for**: Teams using dbt Cloud

#### Setup Steps

1. **Generate dbt Cloud API Token**:
   - Go to dbt Cloud > Account Settings > API Access
   - Create new token with "Read-only" permissions
   - Copy token (save securely)

2. **Configure in DataPulse**:
   ```yaml
   Integrations > Add Integration > dbt Cloud

   Settings:
     Account ID: Your dbt Cloud account ID
     API Token: [paste token]
     Auto-sync: Enabled
     Sync Frequency: After every dbt run
   ```

3. **Test Connection**:
   - Click "Test Connection"
   - Should show: "✅ Connected - Found X projects"

4. **Select Projects**:
   - Choose dbt projects to monitor
   - DataPulse will import:
     - Models
     - Tests
     - Sources
     - Lineage
     - Documentation

#### Automatic Sync

DataPulse syncs automatically:
- After every dbt Cloud job completion
- Via webhook (recommended)
- Or every 1 hour (polling)

**Setup Webhook** (Enterprise):
```yaml
dbt Cloud > Project Settings > Webhooks > Add Webhook

URL: https://api.datapulse.io/webhooks/dbt-cloud
Events:
  - job.succeeded
  - job.failed
  - job.cancelled
```

---

### Method 2: dbt Core (Upload manifest.json)

**Best for**: Teams using dbt Core locally or in CI/CD

#### Manual Upload

1. **Generate manifest.json**:
   ```bash
   dbt compile  # or dbt run
   # Creates target/manifest.json
   ```

2. **Upload to DataPulse**:
   ```yaml
   Integrations > dbt Core > Upload Manifest

   File: target/manifest.json
   Environment: Production
   ```

3. **DataPulse imports**:
   - All models and their dependencies
   - Tests and their configurations
   - Source freshness checks
   - Documentation

#### Automated Sync via API

```python
# In your CI/CD pipeline
import requests

# After dbt run
with open('target/manifest.json', 'rb') as f:
    response = requests.post(
        'https://api.datapulse.io/v1/dbt/manifest',
        headers={'Authorization': f'Bearer {DATAPULSE_API_KEY}'},
        files={'manifest': f},
        data={'environment': 'production'}
    )

print(f"Sync status: {response.json()['status']}")
```

#### GitHub Action Example

```yaml
# .github/workflows/dbt-run.yml
name: dbt Run & Sync DataPulse

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  dbt-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup dbt
        run: pip install dbt-snowflake

      - name: Run dbt
        run: dbt run

      - name: Sync to DataPulse
        run: |
          curl -X POST https://api.datapulse.io/v1/dbt/manifest \
            -H "Authorization: Bearer ${{ secrets.DATAPULSE_API_KEY }}" \
            -F "manifest=@target/manifest.json" \
            -F "environment=production"
```

---

## dbt Test Mapping

DataPulse automatically converts dbt tests to monitors:

### Generic Tests

| dbt Test | DataPulse Monitor | Configuration |
|----------|-------------------|---------------|
| `not_null` | Completeness Monitor | 100% required |
| `unique` | Uniqueness Monitor | 0 duplicates allowed |
| `accepted_values` | Custom SQL Monitor | Check valid values |
| `relationships` | Custom SQL Monitor | Foreign key check |

### Example Conversion

**dbt schema.yml**:
```yaml
models:
  - name: orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null

      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

      - name: customer_id
        tests:
          - relationships:
              to: ref('customers')
              field: customer_id
```

**DataPulse Auto-Creates**:
```yaml
Monitors Created:
  1. orders.order_id_unique
     Type: Uniqueness
     Column: order_id
     Alert: If duplicates found

  2. orders.order_id_not_null
     Type: Completeness
     Column: order_id
     Alert: If NULL values found

  3. orders.status_accepted_values
     Type: Custom SQL
     Query: |
       SELECT COUNT(*) as invalid_count
       FROM orders
       WHERE status NOT IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')
     Alert: If invalid_count > 0

  4. orders.customer_id_relationships
     Type: Custom SQL (Referential Integrity)
     Query: |
       SELECT COUNT(*) as orphaned_count
       FROM orders o
       LEFT JOIN customers c ON o.customer_id = c.customer_id
       WHERE c.customer_id IS NULL
     Alert: If orphaned_count > 0
```

---

## Custom dbt Tests

DataPulse also imports custom/singular tests:

**tests/assert_positive_amounts.sql**:
```sql
-- Assert all order amounts are positive
select
  order_id,
  amount
from {{ ref('orders') }}
where amount <= 0
```

**DataPulse Creates**:
```yaml
Monitor: assert_positive_amounts
Type: Custom SQL
Query: [Same SQL from test]
Alert: If any rows returned
Schedule: Hourly (or custom)
```

---

## Source Freshness Integration

### dbt Source Freshness

**dbt sources.yml**:
```yaml
sources:
  - name: raw
    database: production
    schema: public
    tables:
      - name: orders
        loaded_at_field: _loaded_at
        freshness:
          warn_after: {count: 2, period: hour}
          error_after: {count: 6, period: hour}
```

**DataPulse Auto-Creates**:
```yaml
Monitor: raw.orders_freshness
Type: Freshness
Table: production.public.orders
Timestamp Column: _loaded_at
Thresholds:
  Warning: > 2 hours
  Critical: > 6 hours
Schedule: Every 15 minutes
```

---

## Lineage Integration

### Enhanced Lineage Visualization

DataPulse imports dbt's DAG to show complete lineage:

```
[Source: raw.orders]
        ↓
[dbt model: stg_orders]
        ↓
[dbt model: int_orders_cleaned]
        ↓
[dbt model: fct_orders] ─┬→ [dbt model: daily_revenue]
                          │
                          └→ [dbt model: customer_metrics]
```

### Impact Analysis

When a dbt model fails DataPulse shows:
- Downstream models affected
- Tests that will fail
- BI dashboards using the data
- Estimated users impacted

---

## Monitor Configuration

### Customize dbt Test Monitors

After import, customize monitors in DataPulse:

```yaml
Monitor: orders.order_id_unique (imported from dbt)

Customizations:
  Schedule:
    From: On dbt run (batch)
    To: Every 15 minutes (continuous)

  Alerting:
    Severity: Critical
    Channels: [Slack, PagerDuty]
    Business Hours Only: false

  Advanced:
    Grace Period: 5 minutes
    Alert After: 2 consecutive failures
    Sampling: 10% for tables > 10M rows
```

### Add Additional Monitors

dbt tests are batch (run on schedule). Add continuous monitoring:

```yaml
# Beyond dbt tests, add:

1. Volume Anomaly Detection
   - Detect unexpected row count changes
   - ML-based (learns normal patterns)

2. Distribution Monitoring
   - Track statistical changes
   - Detect outliers

3. Cross-Model Validation
   - Ensure aggregations match
   - Validate business logic
```

---

## Best Practices

### 1. Use dbt for Schema, DataPulse for Runtime

```yaml
dbt Tests (Batch):
  - Schema validation
  - Referential integrity
  - Business logic tests
  - Run during build

DataPulse Monitors (Continuous):
  - Freshness (real-time)
  - Volume anomalies (hourly)
  - Data quality trends (24/7)
  - Production monitoring
```

### 2. Align Environments

```yaml
dbt Environments:
  - dev
  - staging
  - production

DataPulse Data Sources:
  - dev_warehouse (matches dbt dev)
  - staging_warehouse (matches dbt staging)
  - prod_warehouse (matches dbt prod)
```

### 3. Use Tags for Organization

**dbt**:
```yaml
models:
  - name: orders
    tags: [critical, revenue, pii]
```

**DataPulse** imports tags:
```yaml
Monitor: orders_freshness
Tags: [critical, revenue, pii]

Alert Routing (based on tags):
  - critical → PagerDuty
  - revenue → Slack #finance-alerts
  - pii → Email compliance team
```

### 4. Document in dbt, Visualize in DataPulse

```yaml
dbt:
  - Write clear model descriptions
  - Document column meanings
  - Add test rationale

DataPulse:
  - Imports all documentation
  - Shows in lineage view
  - Includes in alerts
```

### 5. Test Coverage Goals

```yaml
Target Test Coverage:
  All models: > 80%
  Critical models: 100%

Minimum Tests per Model:
  - not_null on ID columns
  - unique on primary keys
  - relationships for foreign keys
  - accepted_values for status/enums
```

---

## Troubleshooting

### Tests Not Importing

**Issue**: dbt tests not appearing in DataPulse

**Solutions**:
1. Verify manifest.json is recent:
   ```bash
   dbt compile  # Regenerate manifest
   ```
2. Check test syntax in schema.yml
3. Re-upload manifest or trigger sync
4. Check DataPulse logs for import errors

### Lineage Incomplete

**Issue**: Missing dependencies in lineage

**Solutions**:
1. Ensure all refs() and sources() are used correctly
2. Run `dbt compile` to update manifest
3. Check for circular dependencies
4. Re-sync manifest

### Monitors Failing But dbt Tests Pass

**Issue**: DataPulse monitor fails, but dbt test passes

**Explanation**: Timing difference
- dbt tests run on schedule (e.g., daily)
- DataPulse monitors run continuously (e.g., every 15 min)
- Data may degrade between dbt runs

**Solution**: This is expected and valuable!
- DataPulse catches issues before next dbt run
- Keep both for comprehensive coverage

---

## Advanced: Custom Metadata

### Add Custom Properties

**dbt meta field**:
```yaml
models:
  - name: orders
    meta:
      datapulse:
        monitor_frequency: "*/15 * * * *"  # Every 15 min
        alert_severity: critical
        owner: data-engineering@company.com
        runbook: https://wiki.company.com/orders
```

**DataPulse imports and uses**:
- Sets monitor schedule
- Configures alert severity
- Assigns ownership
- Links runbook

---

## Monitoring dbt Cloud Job Status

**Enterprise Plan Only**

Monitor dbt Cloud jobs themselves:

```yaml
Monitor: dbt Cloud Job Health
Type: Job Monitoring
Checks:
  - Job completion time < 30 minutes
  - Success rate > 95% (last 7 days)
  - No jobs stuck in "Running" state

Alert:
  - If job fails 2 consecutive times
  - If job duration > 45 minutes
  - If queue time > 15 minutes
```

---

## Example: Complete Setup

```yaml
dbt Project:
  Name: analytics
  Models: 120
  Tests: 450
  Environment: Production

DataPulse Integration:
  Method: dbt Cloud API
  Auto-sync: After every run
  Webhook: Enabled

Monitors Auto-Created:
  - From dbt tests: 450 monitors
  - Additional freshness: 30 monitors
  - Additional volume: 60 monitors
  - Total: 540 monitors

Coverage:
  - Models with tests: 115/120 (96%)
  - Critical models: 25/25 (100%)
  - Average tests per model: 3.75

Alert Configuration:
  - Critical models: PagerDuty + Slack
  - Standard models: Slack only
  - Dev/Staging: Email digest

Results (after 3 months):
  - Issues detected: 45
  - Before production impact: 42 (93%)
  - MTTD: 8 minutes (avg)
  - MTTR: 45 minutes (avg)
```

---

## Migration Guide

### Moving from dbt Tests Only to dbt + DataPulse

**Phase 1: Setup** (Week 1)
```yaml
- Connect DataPulse to dbt
- Import manifest
- Review auto-created monitors
- No alerting yet (observation mode)
```

**Phase 2: Baseline** (Week 2-3)
```yaml
- Let monitors run
- Establish baselines
- Tune thresholds
- Identify false positives
```

**Phase 3: Alerting** (Week 4)
```yaml
- Enable alerts for critical models
- Start with email only
- Add Slack after validation
- Add PagerDuty for production
```

**Phase 4: Continuous Improvement** (Ongoing)
```yaml
- Weekly: Review alert volume
- Monthly: Adjust thresholds
- Quarterly: Review coverage
- Add monitors for new models
```

---

## Resources

- dbt Documentation: docs.getdbt.com
- DataPulse dbt Guide: docs.datapulse.io/dbt
- Example Project: github.com/datapulse/dbt-example
- Support: dbt-support@datapulse.io

---

## Need Help?

- dbt integration setup: support@datapulse.io
- Best practices consultation: success@datapulse.io
- dbt-specific questions: See dbt Slack community
