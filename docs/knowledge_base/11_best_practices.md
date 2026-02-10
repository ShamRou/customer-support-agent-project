# Best Practices for Data Observability

## Overview

Learn how to get the most value from DataPulse and build a robust data quality program.

---

## Monitor Setup Best Practices

### Start with Critical Tables

Don't try to monitor everything at once. Focus on:

1. **Revenue-impacting tables**:
   - `orders`, `payments`, `transactions`
   - Tables used in executive dashboards
   - Data feeding billing systems

2. **Compliance-critical data**:
   - Customer PII
   - Financial records
   - Audit logs

3. **High-visibility tables**:
   - Tables used by executives
   - Data in customer-facing products
   - Shared analytics tables

**Action Plan**:
```yaml
Week 1: Top 10 critical tables
Week 2: Add 20 important tables
Week 3: Add remaining production tables
Week 4: Add staging/dev environments
```

### Layer Your Monitoring

Use multiple monitor types for comprehensive coverage:

```yaml
For table: orders
Monitors:
  1. Freshness: Ensure data is current (< 1 hour)
  2. Volume: Detect missing/duplicate data (90k-110k rows/day)
  3. Schema: Track breaking changes
  4. Completeness: Required columns (customer_id, amount, status)
  5. Custom SQL: Business logic validation
     - All amounts > 0
     - Valid status values
     - Foreign key integrity
```

### Set Realistic Thresholds

**❌ Too Strict** (creates alert fatigue):
```yaml
Freshness: < 5 minutes
Volume: Exactly 100,000 rows ± 100
```

**✅ Realistic**:
```yaml
Freshness: < 2 hours (with 15 min grace period)
Volume: 90,000 - 110,000 rows (or use ML anomaly detection)
```

**How to determine thresholds**:
1. Observe patterns for 2 weeks
2. Calculate baseline: p5 to p95
3. Add 20% buffer
4. Enable ML-based detection (Pro+)

---

## Alert Strategy

### Severity Guidelines

| Severity | When to Use | Examples |
|----------|-------------|----------|
| **Critical** | Production SLA breach, revenue impact | Payment processing down, executive dashboard broken |
| **High** | Important data issues, needs quick fix | Missing data in analytics, significant delays |
| **Medium** | Non-urgent issues, can wait | Minor anomalies, informational schema changes |
| **Low** | FYI only, no action needed | Approved schema migrations, volume changes in dev |

### Routing Strategy

```yaml
Critical Alerts:
  - PagerDuty → On-call engineer (immediate)
  - Slack #production-alerts
  - Email to leadership

High Alerts:
  - Slack #data-quality (during business hours)
  - Email to data team

Medium Alerts:
  - Slack #data-quality (batched every 30 min)

Low Alerts:
  - Email digest (daily)
```

### Reduce Alert Fatigue

1. **Use Smart Suppression** (Enterprise):
   ```yaml
   Suppression:
     Auto-suppress downstream impacts: true
     Only alert on root cause: true
   ```

2. **Batch Similar Alerts**:
   ```yaml
   Batching:
     Window: 15 minutes
     Group by: [database, table]
   ```

3. **Business Hours Filtering**:
   ```yaml
   Schedule:
     Suppress: Nights & Weekends (except critical)
     Business Hours: Mon-Fri 8 AM - 6 PM
   ```

4. **Grace Periods**:
   ```yaml
   Alert After: 2 consecutive failures
   Grace Period: 10 minutes
   ```

---

## Incident Management

### Acknowledge Fast, Resolve Thoughtfully

```
Incident Created
    ↓ (Within 5 min)
Acknowledge → Stops escalation
    ↓
Investigate root cause
    ↓
Fix issue
    ↓ (When data is healthy)
Mark Resolved → Add notes
```

### Document Everything

**Good Resolution Notes**:
```
Incident: inc_abc123
Root Cause: ETL job failed due to Snowflake warehouse timeout

Investigation:
1. Checked ETL logs: Connection timeout at 2:15 AM
2. Verified Snowflake warehouse status: Auto-suspended
3. Identified cause: Warehouse auto-suspend timeout too aggressive

Resolution:
1. Increased warehouse auto-suspend to 10 minutes
2. Reran ETL job manually: Completed successfully at 3:45 AM
3. Verified data freshness: Back to normal

Prevention:
1. Updated warehouse configuration
2. Added warehouse status monitor
3. Created runbook: /runbooks/snowflake-timeout

Time to Detect: 12 minutes
Time to Resolve: 1h 30min
```

### Create Runbooks

Link runbooks to monitors:

```yaml
Monitor: orders_freshness_check
Runbook: https://wiki.company.com/runbooks/orders-freshness

Runbook Contents:
  1. What this monitor checks
  2. Common causes of failure
  3. How to investigate
  4. How to fix
  5. Who to escalate to
  6. Related monitors
```

---

## Data Quality Culture

### Make Data Quality Everyone's Responsibility

**Don't**:
- Make data quality "the data team's problem"
- Only care about data quality during incidents

**Do**:
- Include data quality in definition of done
- Review data quality metrics in sprint reviews
- Celebrate data quality improvements

### Implement Quality Gates

```yaml
Pre-Production Checklist:
  ✅ Monitors created for new tables
  ✅ Alerts configured and tested
  ✅ Runbook documented
  ✅ Oncall trained
  ✅ Data quality baseline established
  ✅ Schema changes reviewed
```

### Weekly Data Quality Review

```
Agenda:
1. Review incidents from past week (15 min)
   - Root causes
   - Patterns
   - Recurring issues

2. Monitor health check (10 min)
   - False positive rate
   - Alert volume
   - Threshold tuning needed

3. New table coverage (5 min)
   - What's not monitored yet
   - Prioritize next additions

4. Wins and improvements (5 min)
   - What went well
   - What to continue
```

---

## Performance Optimization

### Monitor Efficiently

**For Large Tables (> 10M rows)**:
1. Enable sampling:
   ```yaml
   Sampling:
     Enabled: true
     Sample Size: 10%
     Min Rows: 10,000,000
   ```

2. Use partition filters:
   ```sql
   -- Instead of full table scan:
   SELECT COUNT(*) FROM large_table;

   -- Use partition filter:
   SELECT COUNT(*) FROM large_table
   WHERE date_partition >= CURRENT_DATE - INTERVAL '7 days';
   ```

3. Add indexes:
   ```sql
   CREATE INDEX idx_created_at ON orders(created_at);
   ```

4. Schedule appropriately:
   ```yaml
   Small tables (<1M rows): Every 15 minutes
   Medium tables (1-10M rows): Hourly
   Large tables (>10M rows): Every 4 hours or daily
   ```

### Optimize Custom SQL Monitors

```sql
-- ❌ Bad (full table scan):
SELECT COUNT(*) as orphaned_orders
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE c.id IS NULL;

-- ✅ Good (indexed columns, partition filter):
SELECT COUNT(*) as orphaned_orders
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE o.created_at >= CURRENT_DATE - INTERVAL '7 days'
  AND c.id IS NULL;
```

---

## Team Organization

### Define Ownership

```yaml
Table: production.orders
Owner: E-commerce Team
Oncall: data-engineering-oncall@company.com
Stakeholders:
  - Finance Team (reporting)
  - Sales Team (dashboards)
  - ML Team (models)

SLA:
  Freshness: < 1 hour
  Uptime: 99.9%
  Support: 24/7
```

### Create a RACI Matrix

| Activity | Data Engineering | Data Analysts | DevOps | Business Teams |
|----------|------------------|---------------|--------|----------------|
| Monitor Setup | **R**esponsible | **C**onsulted | **I**nformed | **C**onsulted |
| Incident Response | **R**esponsible | **C**onsulted | **I**nformed | **I**nformed |
| Threshold Tuning | **A**ccountable | **R**esponsible | - | **C**onsulted |
| Runbook Creation | **R**esponsible | **C**onsulted | **C**onsulted | - |

---

## Integration Best Practices

### dbt Integration

```yaml
Strategy:
  1. Import dbt manifest to DataPulse
  2. Auto-create monitors from dbt tests
  3. Sync daily via API or dbt Cloud webhook

Mapping:
  dbt test: not_null → DataPulse: Completeness Monitor
  dbt test: unique → DataPulse: Uniqueness Monitor
  dbt test: relationships → DataPulse: Custom SQL Monitor
```

### CI/CD Integration

```yaml
# .github/workflows/data-quality.yml
name: Data Quality Checks

on:
  pull_request:
    paths:
      - 'dbt/**'
      - 'airflow/**'

jobs:
  check-quality:
    runs-on: ubuntu-latest
    steps:
      - name: Run DataPulse Checks
        run: |
          # Check if new tables have monitors
          datapulse validate --check-coverage

      - name: Test in Staging
        run: |
          # Run monitors against staging data
          datapulse test --env staging

      - name: Comment on PR
        run: |
          # Add data quality report to PR
          datapulse report --format markdown >> $GITHUB_STEP_SUMMARY
```

### Slack Integration

```yaml
Best Practices:
  - Use dedicated channel: #data-quality
  - Pin important runbooks
  - Create channel topic with oncall info
  - Use threads for incident updates
  - React with ✅ when acknowledged
  - Add 🔍 when investigating
  - Add ✅ when resolved
```

---

## Metrics to Track

### Monitor Your Monitors

```yaml
Key Metrics:
  1. Coverage: % of production tables monitored
     Target: > 95%

  2. Alert Volume: Alerts per day
     Target: < 10 per day (excluding low severity)

  3. False Positive Rate: Invalid alerts / total alerts
     Target: < 10%

  4. MTTD: Mean Time to Detect (when issue starts → alert sent)
     Target: < 15 minutes

  5. MTTR: Mean Time to Resolve (alert sent → issue resolved)
     Target: < 2 hours

  6. Acknowledge Rate: % of alerts acknowledged within 15 min
     Target: > 90%

  7. Data Quality Score: Overall health score
     Target: > 95%
```

### Create a Dashboard

```yaml
Executive Data Quality Dashboard:
  - Overall data quality score (trend)
  - Open incidents by severity
  - MTTR trend (last 30 days)
  - Table coverage %
  - Top 10 noisiest monitors (tune these!)
  - Incidents by team/table
  - Cost of data quality issues (downtime)
```

---

## Scaling DataPulse

### Small Team (1-10 people)

```yaml
Approach:
  - Focus on critical tables only
  - Use automatic ML thresholds
  - Leverage dbt test integration
  - Simple alerting (Slack + Email)

Monitors:
  - 20-50 monitors
  - Default monitor types
  - Weekly reviews
```

### Medium Team (10-50 people)

```yaml
Approach:
  - Dedicated data quality owner
  - Comprehensive table coverage
  - Custom monitors for business logic
  - Advanced routing and suppression

Monitors:
  - 100-500 monitors
  - Mix of default + custom
  - Daily automated reviews
```

### Large Team (50+ people)

```yaml
Approach:
  - Data quality team/practice
  - Full automation and CI/CD
  - Custom dashboards and reports
  - Advanced lineage and impact analysis

Monitors:
  - 500+ monitors
  - Extensive custom SQL
  - Real-time monitoring
  - API-driven workflows
```

---

## Common Pitfalls to Avoid

### 1. Monitor Everything Immediately
❌ **Don't**: Create 500 monitors on day 1
✅ **Do**: Start with 10-20 critical tables, expand gradually

### 2. Set Thresholds Too Strict
❌ **Don't**: Alert on every tiny anomaly
✅ **Do**: Allow reasonable variance, use ML detection

### 3. Ignore False Positives
❌ **Don't**: Let false positives accumulate
✅ **Do**: Tune monitors weekly, maintain <10% false positive rate

### 4. Alert Without Context
❌ **Don't**: Send alerts without runbooks or context
✅ **Do**: Every alert should link to runbook and show impact

### 5. No Ownership
❌ **Don't**: Make alerts no one's responsibility
✅ **Do**: Assign clear owners and oncall rotations

### 6. Set and Forget
❌ **Don't**: Create monitors and never tune them
✅ **Do**: Review monitors monthly, adjust as data patterns change

### 7. Ignore Downstream Impact
❌ **Don't**: Only monitor raw data tables
✅ **Do**: Monitor entire pipeline including reports and dashboards

---

## Success Metrics

### 3 Months After Implementation

✅ Data quality score > 90%
✅ MTTR < 4 hours
✅ 80%+ of production tables monitored
✅ < 5 critical incidents per month
✅ Team trained and comfortable with DataPulse

### 6 Months After Implementation

✅ Data quality score > 95%
✅ MTTR < 2 hours
✅ 95%+ of production tables monitored
✅ < 2 critical incidents per month
✅ Data quality metrics in exec dashboards
✅ Automated quality gates in CI/CD

### 12 Months After Implementation

✅ Data quality score > 98%
✅ MTTR < 1 hour
✅ 100% of production tables monitored
✅ < 1 critical incident per month
✅ Strong data quality culture
✅ Cost savings from prevented incidents

---

## Resources

- [Getting Started Guide](./01_getting_started.md)
- [Monitor Types Reference](./04_monitor_types.md)
- [API Documentation](./08_api_documentation.md)
- [Troubleshooting](./09_troubleshooting_guide.md)

---

## Need Help?

Our Customer Success team can help you:
- Architecture review
- Monitor setup assistance
- Best practices consultation
- Team training

Contact: success@datapulse.io
