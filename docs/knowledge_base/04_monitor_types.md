# Monitor Types in DataPulse

## Overview

DataPulse provides multiple monitor types to ensure comprehensive data quality coverage. Each monitor type serves a specific purpose in maintaining data reliability.

---

## 1. Freshness Monitors

**Purpose**: Ensure your data is updated within expected timeframes.

### How It Works
Freshness monitors check when data was last updated by examining:
- Row timestamps (created_at, updated_at columns)
- Table metadata (last modified time)
- Watermark columns for streaming data

### Configuration
```yaml
Monitor Type: Freshness
Table: orders
Timestamp Column: created_at
Expected Freshness: 1 hour
Alert Threshold: > 2 hours
```

### Use Cases
- Ensuring ETL jobs complete on time
- Monitoring streaming data pipelines
- Detecting stale data in dashboards
- SLA compliance for data delivery

### Best Practices
- Set thresholds based on your SLA requirements
- Use business hours awareness for batch jobs
- Configure grace periods for weekend/holiday data

---

## 2. Volume Monitors

**Purpose**: Detect anomalies in data volume (row counts).

### How It Works
Volume monitors track row counts over time and use ML to detect:
- Unexpected spikes in data
- Missing or incomplete data loads
- Data duplication issues

### Configuration
```yaml
Monitor Type: Volume
Table: user_events
Comparison: Day over day
Expected Range: 90,000 - 110,000 rows
Anomaly Sensitivity: Medium
```

### Detection Methods
- **Static Thresholds**: Define exact min/max row counts
- **Relative Changes**: Alert on X% change from previous period
- **ML-Based**: Automatic anomaly detection using historical patterns (Pro+)

### Use Cases
- Detecting incomplete data loads
- Identifying data pipeline failures
- Catching duplicate data issues
- Monitoring seasonal patterns

---

## 3. Schema Monitors

**Purpose**: Track and alert on schema changes.

### How It Works
Schema monitors detect:
- New columns added
- Columns removed
- Data type changes
- Column renames
- Constraint modifications

### Configuration
```yaml
Monitor Type: Schema
Table: customer_data
Alert On:
  - Column Drops: true
  - Type Changes: true
  - New Columns: false (info only)
Approval Required: true
```

### Use Cases
- Preventing breaking changes in production
- Tracking schema evolution over time
- Ensuring downstream compatibility
- Compliance and audit requirements

### Schema Change Workflow
1. Change detected automatically
2. Alert sent to data team
3. Review and approve/reject in DataPulse UI
4. Document change reason
5. Notify downstream consumers

---

## 4. Custom SQL Monitors

**Purpose**: Create custom validation rules using SQL queries.

**Available on**: Pro and Enterprise plans

### How It Works
Write any SQL query that returns a single numeric value. DataPulse evaluates the result against your threshold.

### Example: Null Check
```sql
SELECT COUNT(*) as null_count
FROM users
WHERE email IS NULL
```
Alert if `null_count > 0`

### Example: Referential Integrity
```sql
SELECT COUNT(*) as orphaned_orders
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE c.id IS NULL
```
Alert if `orphaned_orders > 0`

### Example: Data Range Validation
```sql
SELECT AVG(price) as avg_price
FROM products
WHERE category = 'electronics'
```
Alert if `avg_price < 50 OR avg_price > 5000`

### Example: Business Logic
```sql
SELECT COUNT(*) as negative_quantity
FROM inventory
WHERE quantity < 0
```
Alert if `negative_quantity > 0`

### Best Practices
- Keep queries performant (add indexes if needed)
- Use query timeout limits
- Test queries before deploying
- Add comments explaining the validation logic

---

## 5. Distribution Monitors

**Purpose**: Track statistical distributions of numeric columns.

**Available on**: Pro and Enterprise plans

### How It Works
Monitors statistical metrics:
- Mean, median, mode
- Standard deviation
- Min/max values
- Percentiles (p50, p95, p99)
- Outlier detection

### Configuration
```yaml
Monitor Type: Distribution
Table: transactions
Column: amount
Metrics:
  - Mean: 500 ± 100
  - P99: < 10000
  - Min: > 0
```

### Use Cases
- Detecting pricing errors
- Monitoring transaction patterns
- Identifying data quality issues
- Catching data entry mistakes

---

## 6. Uniqueness Monitors

**Purpose**: Ensure columns that should be unique remain unique.

### How It Works
Checks for duplicate values in specified columns or column combinations.

### Configuration
```yaml
Monitor Type: Uniqueness
Table: users
Columns: [email]
Allow Duplicates: false
```

### Use Cases
- Primary key validation
- Email uniqueness in user tables
- Preventing duplicate transactions
- Ensuring data integrity

---

## 7. Completeness Monitors

**Purpose**: Track null rates and data completeness.

### How It Works
Monitors the percentage of null/empty values in columns.

### Configuration
```yaml
Monitor Type: Completeness
Table: customer_profiles
Required Columns:
  - first_name: 100% required
  - last_name: 100% required
  - phone: 80% required (optional for some users)
```

### Use Cases
- Ensuring required fields are populated
- Tracking data collection quality
- Identifying form completion issues
- Meeting compliance requirements

---

## 8. Timeliness Monitors

**Purpose**: Ensure data arrives within expected time windows.

**Available on**: Enterprise plan

### How It Works
Tracks end-to-end latency from source to destination:
- Source extraction time
- Transformation duration
- Load completion time
- Total pipeline latency

### Use Cases
- SLA monitoring
- Pipeline performance tracking
- Identifying bottlenecks
- Capacity planning

---

## 9. Cross-Table Monitors

**Purpose**: Validate relationships between tables.

**Available on**: Enterprise plan

### Configuration
```sql
-- Ensure orders match sum of order_items
SELECT
  o.order_id,
  o.total_amount,
  SUM(oi.item_price * oi.quantity) as calculated_total
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.total_amount
HAVING ABS(o.total_amount - calculated_total) > 0.01
```

### Use Cases
- Referential integrity
- Aggregate validation
- Multi-table consistency checks
- Complex business rules

---

## Choosing the Right Monitor

| Data Issue | Recommended Monitor |
|------------|-------------------|
| Data not updating | Freshness |
| Missing records | Volume |
| Breaking changes | Schema |
| Invalid values | Custom SQL |
| Null in required fields | Completeness |
| Duplicate records | Uniqueness |
| Outliers/anomalies | Distribution |
| Complex validation | Custom SQL |
| Cross-table issues | Cross-Table |

---

## Monitor Scheduling

All monitors support flexible scheduling:
- **Continuous**: Check every 5/15/30 minutes
- **Hourly**: On the hour or specific minutes
- **Daily**: Specific time with timezone support
- **Weekly**: Specific days and times
- **Custom Cron**: Advanced scheduling

---

## Need Help?

See our [Alerts & Notifications Guide](./05_alerts_notifications.md) to configure how you receive monitor alerts.
