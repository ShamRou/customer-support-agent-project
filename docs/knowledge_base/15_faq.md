# Frequently Asked Questions (FAQ)

## General Questions

### What is DataPulse?

DataPulse is a data observability platform that monitors your data pipelines, detects quality issues, and alerts you before problems impact your business. Think of it as "monitoring for your data" - similar to how you monitor application uptime, DataPulse monitors data quality, freshness, and reliability.

### How is DataPulse different from dbt tests?

| Feature | dbt Tests | DataPulse |
|---------|-----------|-----------|
| **When** | Batch (during dbt runs) | Continuous (24/7) |
| **Scope** | Transformation layer | End-to-end pipeline |
| **Detection** | On dbt run completion | Real-time |
| **Alerting** | Basic (pass/fail) | Advanced (routing, severity, ML) |
| **Coverage** | dbt models only | All tables (raw + transformed) |
| **Best Use** | Build-time validation | Production monitoring |

**Recommendation**: Use both! dbt tests for build-time validation, DataPulse for continuous production monitoring.

### What data sources do you support?

**Fully Supported**:
- Snowflake
- Google BigQuery
- Amazon Redshift
- Databricks
- PostgreSQL
- MySQL
- Amazon Athena

**Coming Soon**:
- Microsoft Azure Synapse
- Oracle
- Teradata
- ClickHouse

**Request Integration**: support@datapulse.io

### Does DataPulse store my data?

**What we store**:
- Table/column metadata (names, types, sizes)
- Data quality metrics (row counts, null percentages)
- Query results from monitors (aggregated values only)
- Audit logs

**What we DON'T store**:
- Raw table data
- Customer PII (except in monitor query results)
- Full table contents
- Your actual business data

DataPulse only reads metadata and runs aggregation queries. Your data stays in your warehouse.

---

## Pricing & Plans

### What's included in the Free plan?

```yaml
Free Plan ($0/month):
  ✅ Up to 5 data sources
  ✅ Up to 10 monitors
  ✅ 7 days data retention
  ✅ Email notifications
  ✅ Community support
  ✅ Basic monitor types (freshness, volume, schema)

  ❌ No API access
  ❌ No custom SQL monitors
  ❌ No Slack/PagerDuty integrations
  ❌ No ML anomaly detection
```

### Can I try Pro features before upgrading?

Yes! All new users get a **14-day free trial** of Pro features. No credit card required.

### How does billing work?

```yaml
Billing:
  Cycle: Monthly or Annual
  Annual Discount: 20% off
  Payment: Credit card, ACH, wire (Enterprise)
  Invoicing: Available for Enterprise
  Overages: Pro only (API requests)

Changes:
  Upgrades: Immediate (prorated)
  Downgrades: End of billing cycle
  Cancellation: Anytime (no penalty)
```

### What if I exceed my API limit (Pro plan)?

```yaml
Pro Plan API:
  Included: 10,000 requests/month
  Overage: $10 per 10,000 additional requests
  Alert: At 80% usage
  Tracking: Real-time in dashboard

Enterprise Plan:
  API: Unlimited (no overages)
```

### Do you offer non-profit or educational discounts?

Yes! Contact sales@datapulse.io with:
- Organization details
- 501(c)(3) status (US) or equivalent
- Use case
- Number of users

Typical discount: 30-50% off

---

## Setup & Integration

### How long does setup take?

**Typical Timeline**:
```yaml
Connection Setup: 15 minutes
  - Create read-only user
  - Configure network access
  - Test connection

Initial Monitoring: 30 minutes
  - Select tables to monitor
  - Review auto-created monitors
  - Configure alerting

Fine-Tuning: 1-2 weeks
  - Observe patterns
  - Adjust thresholds
  - Reduce false positives

Full Deployment: 4-6 weeks
  - Cover all tables
  - Integrate with workflows
  - Train team
```

### Do I need to install anything?

No! DataPulse is 100% cloud-based (SaaS). No installation required.

**What you need**:
- Web browser (Chrome, Firefox, Safari, Edge)
- Network access to your data warehouse
- Read-only database credentials

### Can DataPulse work with on-premise databases?

**Options**:

1. **VPN/SSH Tunnel** (Pro):
   - Connect via secure tunnel
   - DataPulse connects through your VPN

2. **Private Deployment** (Enterprise):
   - DataPulse deployed in your VPC/network
   - No external connectivity required

3. **Self-Hosted** (Enterprise):
   - On-premise installation
   - Full control over infrastructure

Contact sales@datapulse.io for Enterprise options.

### What permissions does DataPulse need?

**Minimum Required**:
```sql
-- Read access to tables
GRANT SELECT ON database.schema.* TO datapulse_user;

-- Read access to metadata
GRANT SELECT ON information_schema.* TO datapulse_user;

-- Ability to run queries
GRANT USAGE ON WAREHOUSE compute_wh TO datapulse_user;
```

**NOT Required**:
- Write access (INSERT, UPDATE, DELETE)
- Admin privileges
- Schema modification
- User management

**Best Practice**: Use dedicated read-only service account.

---

## Monitors & Alerts

### How many monitors should I create?

**General Guidance**:
```yaml
Per Table:
  Minimum: 2-3 monitors (freshness, volume, schema)
  Recommended: 3-5 monitors (add completeness, custom validation)
  Maximum: No limit (but avoid over-monitoring)

By Table Priority:
  Critical (Tier 1): 5+ monitors, 15-min checks
  Important (Tier 2): 3-4 monitors, hourly checks
  Standard (Tier 3): 2-3 monitors, daily checks
  Dev/Testing: 1-2 monitors, as needed
```

### What's a good false positive rate?

**Target**: <10% false positives

**Calculation**:
```
False Positive Rate = (Invalid Alerts / Total Alerts) × 100

Example:
  Total Alerts: 100
  False Positives: 8
  Rate: 8% ✅ Good
```

**If >10%**: Tune thresholds, use ML anomaly detection, add grace periods.

### How do I reduce alert fatigue?

**Strategies**:
```yaml
1. Use Alert Batching:
   Combine multiple alerts into digest

2. Set Appropriate Severity:
   Not everything is critical

3. Enable Smart Suppression:
   Only alert on root cause

4. Use Business Hours:
   Suppress non-critical during off-hours

5. Add Grace Periods:
   Alert after 2 consecutive failures

6. Tune Thresholds:
   Weekly review and adjustment

7. Use ML Detection:
   Reduce false positives automatically
```

### Can I customize alert messages?

Yes! (Enterprise)

```yaml
Alert Template:
  Title: "🚨 {{ severity | upper }}: {{ monitor.name }}"
  Body: |
    **Issue**: {{ issue_description }}
    **Table**: {{ resource.database }}.{{ resource.table }}
    **Expected**: {{ threshold }}
    **Actual**: {{ actual_value }}

    **Runbook**: {{ runbook_url }}
    **Owner**: {{ owner.email }}

    [View Details]({{ incident_url }})
```

---

## Security & Compliance

### Is DataPulse SOC 2 compliant?

Yes! DataPulse is SOC 2 Type II certified.

**Report Access**: Available to Enterprise customers via NDA.

### Is DataPulse GDPR compliant?

Yes! DataPulse is fully GDPR compliant.

**Features**:
- Data Processing Agreement (DPA) available
- EU data residency option
- Right to access/delete data
- Privacy by design

### Do you offer a BAA for HIPAA compliance?

Yes! (Enterprise only)

Contact: hipaa@datapulse.io

**Includes**:
- Business Associate Agreement
- PHI encryption
- Audit logging
- Access controls

### Where is my data stored?

**Default**: US East (N. Virginia)

**Available Regions** (Enterprise):
- 🇺🇸 US East, US West
- 🇪🇺 EU (Frankfurt, Ireland)
- 🇬🇧 UK (London)
- 🇨🇦 Canada (Montreal)
- 🇦🇺 Asia Pacific (Sydney)

### How is my data encrypted?

**In Transit**:
- TLS 1.3
- Perfect forward secrecy
- Certificate pinning

**At Rest**:
- AES-256 encryption
- Encrypted backups
- AWS KMS key management (Enterprise: BYOK supported)

---

## Technical Questions

### How often do monitors run?

**Configurable**:
```yaml
Options:
  - Every 5 minutes
  - Every 15 minutes (recommended for freshness)
  - Every 30 minutes
  - Hourly (recommended for volume)
  - Daily (recommended for large tables)
  - Weekly
  - Custom cron expression

Best Practice:
  Freshness: Every 15 minutes
  Volume: Hourly
  Schema: On change
  Custom SQL: Based on complexity
```

### Does monitoring impact warehouse performance?

**Minimal Impact**:
```yaml
Design:
  - Efficient queries (aggregations only)
  - Query result caching
  - Partition-aware querying
  - Sampling for large tables

Typical Cost:
  Per Monitor: $0.01 - $0.10/day
  100 Monitors: $1 - $10/day
  Compare to: Warehouse costs ($100s-$1000s/day)

Recommendation:
  - Use dedicated small warehouse
  - Schedule expensive monitors off-peak
  - Enable sampling for large tables
```

### Can DataPulse detect data drift?

Yes! Multiple ways:

1. **Distribution Monitoring**: Tracks statistical changes
2. **ML Anomaly Detection**: Learns normal patterns, alerts on drift
3. **Schema Monitoring**: Detects structural changes
4. **Custom SQL**: Write specific drift detection queries

### How does ML anomaly detection work?

See our [Machine Learning Features Guide](./14_machine_learning_features.md) for details.

**Summary**:
1. Train on 14+ days of data
2. Learn patterns (daily, weekly, seasonal)
3. Predict expected values
4. Alert when actual significantly deviates
5. Continuously adapt to changes

---

## Troubleshooting

### Why am I not receiving alerts?

**Checklist**:
```yaml
✅ Monitor is active (not paused)
✅ Monitor is scheduled correctly
✅ Notification channel configured
✅ Email verified / Slack authorized
✅ Not in spam folder
✅ Alert routing includes your channel
✅ Severity meets routing criteria
✅ No suppression rules blocking alerts
```

**Test**:
- Settings > Notifications > Send Test Alert

### Why is my monitor failing?

**Common Causes**:
```yaml
Connection Issues:
  - Data source disconnected
  - Credentials expired
  - Network access blocked

Permission Issues:
  - Missing SELECT privilege
  - Table access revoked
  - Warehouse access removed

Configuration Issues:
  - Table doesn't exist
  - Column renamed
  - Wrong timestamp column
  - Invalid threshold

Data Issues:
  - No data in table
  - All NULLs in timestamp column
  - Unexpected data format
```

**Debug**:
- Monitor Details > Execution History > View Error

### How do I contact support?

| Plan | Support Channels | Response Time |
|------|------------------|---------------|
| **Free** | Community forum | Best effort |
| **Pro** | Email, In-app chat (9-5 EST) | < 24 hours |
| **Enterprise** | Email, Chat (24/7), Phone, Slack | < 4 hours |

**Contact**:
- Email: support@datapulse.io
- Chat: In-app (bottom right)
- Phone: (Enterprise) +1-800-DATAPULSE
- Community: community.datapulse.io

---

## Best Practices

### What should I monitor first?

**Priority Order**:
```yaml
1. Revenue-Critical Tables:
   - orders, payments, transactions
   - Executive dashboard sources
   - Customer-facing data

2. Compliance Tables:
   - PII data
   - Financial records
   - Audit logs

3. High-Visibility Tables:
   - Shared analytics tables
   - Report sources
   - ML model inputs

4. Everything Else:
   - Staging tables
   - Internal analytics
   - Development data
```

### How do I know if DataPulse is working?

**Health Checks**:
```yaml
Daily:
  - Check dashboard (any critical alerts?)
  - Review recent incidents (all resolved?)

Weekly:
  - Alert volume reasonable? (<10/day)
  - False positive rate low? (<10%)
  - Monitors running successfully? (>95%)

Monthly:
  - Data quality score trending up? (>95%)
  - Coverage increasing? (>90% of tables)
  - MTTR decreasing? (<2 hours)
```

### Should I use DataPulse in dev/staging?

**Yes!** Recommended strategy:

```yaml
Development:
  - Basic monitoring only
  - Low severity alerts
  - Email notifications
  - Learn patterns

Staging:
  - Mirror production monitors
  - Test before prod deploy
  - Medium severity
  - Slack notifications

Production:
  - Full monitoring
  - Appropriate severity
  - PagerDuty for critical
  - 24/7 coverage
```

---

## Still Have Questions?

- **Documentation**: docs.datapulse.io
- **Community**: community.datapulse.io
- **Support**: support@datapulse.io
- **Sales**: sales@datapulse.io
- **Status**: status.datapulse.io

---

## Helpful Resources

- [Getting Started Guide](./01_getting_started.md)
- [Integration Guides](./02_snowflake_integration.md)
- [Monitor Types](./04_monitor_types.md)
- [Best Practices](./11_best_practices.md)
- [Troubleshooting](./09_troubleshooting_guide.md)
