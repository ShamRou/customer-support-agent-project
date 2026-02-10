# Data Lineage

## Overview

Data lineage in DataPulse provides end-to-end visibility into how data flows through your systems, from source to destination. Understand dependencies, track impact, and troubleshoot issues faster.

**Available on**: Pro and Enterprise plans

---

## What is Data Lineage?

Data lineage tracks:
- **Source systems**: Where data originates
- **Transformations**: How data is processed and transformed
- **Dependencies**: Which tables, views, and jobs depend on each other
- **Downstream consumers**: Who uses the data (dashboards, reports, ML models)
- **Impact analysis**: What breaks if this data source fails

---

## Lineage Visualization

### Table-Level Lineage

View how tables are connected:

```
[Source DB: orders]
        ↓
[ETL Job: daily_orders_etl]
        ↓
[DW: fact_orders] ─┬→ [View: daily_revenue]
                    │       ↓
                    │   [Dashboard: Revenue Dashboard]
                    │
                    └→ [ML Model: churn_prediction]
```

### Column-Level Lineage (Enterprise)

Track how specific columns flow and transform:

```
orders.customer_id
        ↓
    [JOIN customers]
        ↓
fact_orders.customer_key
        ↓
    [AGGREGATE]
        ↓
customer_metrics.total_orders
```

---

## How DataPulse Builds Lineage

### 1. Automatic Discovery

DataPulse automatically discovers lineage from:

#### Query Logs Analysis
```sql
-- DataPulse parses your warehouse query logs:
CREATE TABLE fact_sales AS
SELECT
  o.order_id,
  c.customer_name,
  p.product_name,
  o.amount
FROM raw.orders o
JOIN raw.customers c ON o.customer_id = c.id
JOIN raw.products p ON o.product_id = p.id;
```

Result: Lineage shows `fact_sales` depends on `orders`, `customers`, and `products`.

#### Schema Metadata
- Foreign key relationships
- View definitions
- Materialized view dependencies

#### ETL Tool Integration
- dbt: Parses manifest.json
- Airflow: Analyzes DAGs
- Fivetran/Airbyte: Connector mappings
- Spark: Reads execution plans

### 2. Manual Annotations

Add custom lineage for:
- External systems
- Manual processes
- Legacy pipelines
- BI tools

```yaml
Custom Lineage:
  - Source: Salesforce (External)
    Process: Fivetran Sync
    Destination: raw.salesforce_accounts
    Frequency: Every 15 minutes

  - Source: fact_orders
    Process: Python Script (weekly_report.py)
    Destination: Google Sheets: Sales Report
    Owner: sales-team@company.com
```

---

## Features

### Impact Analysis

**Question**: "What happens if table X fails?"

DataPulse shows:
- Downstream tables that will be affected
- Dashboards that will break
- ML models that will fail
- Number of end users impacted

**Example**:
```
If `raw.orders` fails:
  ⚠️ 5 downstream tables affected
  ⚠️ 3 dashboards will break
  ⚠️ 2 ML models will fail
  ⚠️ ~150 users impacted

Affected Resources:
  - fact_orders (critical)
  - daily_revenue_summary (high)
  - customer_metrics (medium)
  - Dashboard: Executive Revenue (critical)
  - Dashboard: Sales Performance (high)
```

### Root Cause Analysis

**Question**: "Why is this dashboard showing stale data?"

DataPulse traces backward:
```
[Dashboard: Revenue Dashboard] ❌ Stale
        ↑
[View: daily_revenue] ✅ OK
        ↑
[Table: fact_orders] ❌ Stale (4 hours old)
        ↑
[ETL Job: orders_etl] ❌ Failed at 2 AM
        ↑
[Source: raw.orders] ✅ OK
```

**Root Cause**: ETL job failure

### Data Quality Propagation

When a monitor fails, DataPulse shows downstream impact:

```
Monitor Alert: orders.freshness_check FAILED

Downstream Impact:
  • fact_orders (dependent)
    Status: Will become stale in 30 minutes
    Action: Monitor auto-suppressed

  • daily_revenue (2 levels down)
    Status: Will be affected in 1 hour
    Action: Stakeholders notified

  • Revenue Dashboard (3 levels down)
    Status: Will show stale data
    Action: Warning banner added
```

---

## Lineage Graph Navigation

### Interactive Visualization

```
Controls:
  🔍 Zoom: In/Out/Fit
  🖱️  Pan: Click and drag
  🎯 Focus: Click node to center
  🔄 Refresh: Update with latest metadata
  📊 Layers: Show/hide table types
```

### Filter Options

```yaml
Filters:
  Show:
    - Tables: ✓
    - Views: ✓
    - Materialized Views: ✓
    - External Tables: ✓
    - BI Dashboards: ✓
    - ML Models: ✗

  Direction:
    - Upstream: 3 levels
    - Downstream: 2 levels

  Relationships:
    - Direct only: ✗
    - Include indirect: ✓
```

### Search & Jump

- Search for any table/view
- Jump to definition
- View query that created it
- See last update time
- Check data quality status

---

## Integration with Monitoring

### Smart Alert Suppression

When a source table fails:
```yaml
Primary Alert:
  Table: raw.orders
  Monitor: freshness_check
  Status: FAILED
  Severity: Critical

Auto-Suppressed (downstream):
  - fact_orders.freshness_check
  - daily_revenue.volume_check

Reason: Root cause is upstream (raw.orders)
Action: Only alert on root cause, suppress downstream noise
```

### Incident Context

Every alert includes lineage context:

```
Alert: fact_orders freshness check failed

Lineage Context:
  Upstream (sources):
    ✅ raw.orders (healthy)
    ✅ raw.customers (healthy)
    ❌ raw.products (stale - likely root cause)

  Downstream (consumers):
    ⚠️ daily_revenue (will be affected)
    ⚠️ Executive Dashboard (3 users)
    ⚠️ churn_model (low priority)

Recommended Action: Fix raw.products first
```

---

## dbt Integration

### Automatic dbt Lineage

DataPulse parses dbt projects:

1. **Connect dbt**:
   ```yaml
   Settings > Integrations > dbt Cloud
   - Or upload manifest.json for dbt Core
   ```

2. **Automatic Discovery**:
   - Model dependencies
   - Source declarations
   - Test definitions
   - Documentation
   - Tags and metadata

3. **Enhanced Lineage**:
   ```
   [Source: raw.orders]
          ↓
   [dbt model: stg_orders]
          ↓
   [dbt model: int_orders_enriched]
          ↓
   [dbt model: fct_orders]
   ```

### dbt Test Integration

DataPulse syncs with dbt tests:

```yaml
dbt Tests → DataPulse Monitors

dbt:
  - not_null: customer_id
  - unique: order_id
  - relationships: product_id → products.id

DataPulse Auto-Creates:
  - Completeness Monitor: customer_id
  - Uniqueness Monitor: order_id
  - Referential Integrity Monitor: orders → products
```

---

## API Access (Enterprise)

Query lineage programmatically:

```python
from datapulse import Client

client = Client(api_key="your_api_key")

# Get upstream dependencies
upstream = client.lineage.get_upstream(
    table="production.fact_orders",
    levels=3
)

# Get downstream consumers
downstream = client.lineage.get_downstream(
    table="production.raw_orders",
    levels=5
)

# Impact analysis
impact = client.lineage.analyze_impact(
    table="production.raw_orders",
    scenario="data_loss"
)

print(f"Tables affected: {impact.affected_tables}")
print(f"Users impacted: {impact.estimated_users}")
print(f"Dashboards broken: {impact.broken_dashboards}")
```

---

## Column-Level Lineage (Enterprise)

Track individual columns through transformations:

### Example: Customer Email Lineage

```
salesforce.contacts.Email
        ↓
raw.sf_contacts.email
        ↓ [lowercase transformation]
staging.contacts.email_normalized
        ↓ [join + select]
dim_customers.email
        ↓ [aggregate]
customer_segments.primary_email
        ↓
[Dashboard Filter: Customer Email Search]
```

### Transformation Tracking

```sql
-- DataPulse tracks transformations:
SELECT
  LOWER(TRIM(email)) as email_normalized,  -- Tracks: lowercase, trim
  CONCAT(first_name, ' ', last_name) as full_name,  -- Tracks: concat
  CAST(created_at AS DATE) as signup_date  -- Tracks: type conversion
FROM raw.contacts;
```

### PII Tracking (Enterprise)

Automatically identify and track PII:

```yaml
PII Columns Detected:
  - customers.email (email address)
  - customers.phone (phone number)
  - customers.ssn (sensitive - encrypted)
  - orders.credit_card_last_4 (PCI data)

Downstream PII Propagation:
  ✓ Tracks where PII is copied
  ✓ Identifies joins that expose PII
  ✓ Alerts on PII in non-compliant locations
  ✓ Audit trail for compliance
```

---

## Business Context

Add business metadata to lineage:

```yaml
Table: fact_orders
Business Context:
  Owner: Data Engineering Team
  Stakeholders:
    - Sales Team (dashboard consumers)
    - Finance Team (reporting)
    - ML Team (churn prediction)

  SLA:
    Freshness: < 1 hour
    Availability: 99.9%
    Priority: Critical

  Cost:
    Storage: $150/month
    Query: $500/month
    Total: $650/month

  Certifications:
    - Production Ready: ✓
    - Documentation Complete: ✓
    - Data Quality Monitored: ✓
    - SOC 2 Compliant: ✓
```

---

## Lineage Export

Export lineage for documentation or external tools:

```bash
# Export formats
- JSON: Full lineage graph
- CSV: Edge list (source → target)
- GraphML: Import to graph tools
- PNG/SVG: Visual diagram
- Markdown: Documentation

# Export via UI or API
datapulse lineage export \
  --table production.fact_orders \
  --format json \
  --output lineage.json
```

---

## Best Practices

1. **Keep Metadata Fresh**: Enable automatic sync (hourly recommended)
2. **Tag Critical Resources**: Mark production tables, tier-1 dashboards
3. **Document Ownership**: Assign teams to tables
4. **Use Column Lineage for PII**: Track sensitive data flow
5. **Regular Lineage Audits**: Monthly review of dependencies
6. **Integrate with dbt**: Leverage dbt's lineage + tests
7. **Set Up Impact Alerts**: Notify stakeholders of upstream failures

---

## Troubleshooting

### Missing Lineage

**Issue**: Some dependencies not showing

**Solutions**:
- Enable query log analysis
- Upload dbt manifest
- Add manual lineage entries
- Check permissions (DataPulse needs read access to metadata)

### Outdated Lineage

**Issue**: Lineage doesn't reflect recent changes

**Solutions**:
- Click "Refresh Lineage" in UI
- Enable automatic sync (Settings > Lineage > Auto-sync)
- Check last sync timestamp

### Performance Issues

**Issue**: Lineage graph slow to load

**Solutions**:
- Limit upstream/downstream levels
- Filter by table type
- Focus on specific subgraph
- Use search instead of full graph

---

## Need Help?

- See [API Documentation](./08_api_documentation.md) for programmatic access
- Contact support@datapulse.io for Enterprise features
- Join our Slack community for tips
