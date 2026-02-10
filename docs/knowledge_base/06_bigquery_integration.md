# Google BigQuery Integration Guide

## Overview

Connect DataPulse to Google BigQuery to monitor your data warehouse with automatic data quality checks, schema tracking, and anomaly detection.

## Prerequisites

- Active Google Cloud Platform (GCP) account
- BigQuery datasets you want to monitor
- DataPulse Pro or Enterprise plan
- Project Editor or BigQuery Admin role

---

## Setup Methods

### Method 1: Service Account (Recommended)

#### Step 1: Create Service Account

1. Open [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **IAM & Admin** > **Service Accounts**
3. Click **Create Service Account**
4. Name: `datapulse-monitor`
5. Grant roles:
   - **BigQuery Data Viewer**
   - **BigQuery Job User**
   - **BigQuery Metadata Viewer**

#### Step 2: Generate Key

1. Click on the service account
2. Go to **Keys** tab
3. Click **Add Key** > **Create New Key**
4. Choose **JSON** format
5. Download the key file (keep it secure!)

#### Step 3: Configure in DataPulse

1. Navigate to **Integrations** > **Add Integration**
2. Select **BigQuery**
3. Choose **Service Account Authentication**
4. Upload your JSON key file
5. Enter your **Project ID**
6. Click **Test Connection**
7. Save when successful

---

### Method 2: OAuth (User-Based)

1. In DataPulse, select **BigQuery** integration
2. Choose **OAuth Authentication**
3. Click **Authorize with Google**
4. Sign in with your Google account
5. Grant necessary permissions
6. Select Project ID

**Note**: OAuth is simpler but service accounts are more secure for production use.

---

## Granting Permissions

### Dataset-Level Access

To limit access to specific datasets:

```sql
-- Grant access to a single dataset
GRANT `roles/bigquery.dataViewer`
ON SCHEMA `project-id.dataset_name`
TO "serviceAccount:datapulse-monitor@project-id.iam.gserviceaccount.com";
```

### Table-Level Access

For fine-grained control:

```sql
-- Grant access to specific tables
GRANT `roles/bigquery.dataViewer`
ON TABLE `project-id.dataset_name.table_name`
TO "serviceAccount:datapulse-monitor@project-id.iam.gserviceaccount.com";
```

---

## Selecting Tables to Monitor

After connecting:

1. You'll see all accessible projects and datasets
2. Expand datasets to view tables
3. Select tables you want to monitor
4. DataPulse will:
   - Analyze table structure
   - Identify partition columns
   - Establish baseline metrics
   - Create default monitors

---

## Cost Optimization

### 1. Use Partitioned Tables

DataPulse automatically detects partitioned tables and queries only recent partitions:

```sql
-- DataPulse optimizes queries like this:
SELECT COUNT(*) as row_count
FROM `project.dataset.table`
WHERE _PARTITIONTIME >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY);
```

### 2. Configure Sampling

For large tables, enable sampling:

```yaml
Monitor Settings:
  Sampling:
    Enabled: true
    Method: Random
    Sample Size: 10%  # Query 10% of data
    Min Rows: 1000000 # Only sample if table > 1M rows
```

### 3. Set Query Limits

```yaml
Query Settings:
  Max Bytes Scanned: 10 GB per query
  Max Cost Per Day: $5.00
  Alert on Limit: 80%
```

### 4. Schedule Wisely

Run expensive monitors during off-peak hours:

```yaml
Monitor Schedule:
  Large Table Monitors: 2 AM UTC
  Standard Monitors: Every 15 minutes
  Custom SQL: Hourly
```

---

## Monitoring Partitioned Tables

DataPulse provides special handling for partitioned tables:

### Time-Based Partitioning

```yaml
Monitor Type: Freshness
Table: events (partitioned by event_date)
Settings:
  Partition Column: event_date
  Check Latest Partition: true
  Expected Freshness: 2 hours
```

### Ingestion-Time Partitioning

```yaml
Monitor Type: Volume
Table: logs (ingestion-time partitioned)
Settings:
  Use _PARTITIONTIME: true
  Compare: Current vs Previous Day
  Anomaly Sensitivity: Medium
```

---

## Monitoring Clustered Tables

For clustered tables, DataPulse optimizes queries using cluster columns:

```yaml
Table: user_events
Partitioned By: event_date
Clustered By: [user_id, event_type]

# DataPulse automatically uses clustering:
WHERE event_date = CURRENT_DATE()
  AND event_type = 'purchase'  # Efficient due to clustering
```

---

## BigQuery-Specific Monitors

### Slot Usage Monitoring

**Enterprise Plan Only**

Track query performance and slot utilization:

```yaml
Monitor Type: Performance
Metric: Slot Utilization
Threshold:
  Warning: > 80%
  Critical: > 95%
Alert: Slack #data-engineering
```

### Cost Monitoring

**Enterprise Plan Only**

Monitor BigQuery costs:

```yaml
Monitor Type: Cost
Aggregation: Daily
Threshold:
  Daily: > $100
  Monthly: > $2500
Breakdown:
  - By Project
  - By Dataset
  - By User
```

### Query Performance

Track slow queries:

```yaml
Monitor Type: Query Performance
Thresholds:
  Duration: > 30 seconds
  Bytes Scanned: > 1 TB
  Slot Time: > 10 minutes
Action: Log slow queries for review
```

---

## Advanced Features

### Cross-Region Monitoring

Monitor datasets across multiple regions:

```yaml
Projects:
  - project-us: us-central1
  - project-eu: europe-west1
  - project-asia: asia-east1

Settings:
  Consolidate Alerts: true
  Region-Aware Scheduling: true
```

### Materialized View Monitoring

Track materialized view freshness:

```yaml
Monitor Type: Materialized View
View: mv_daily_revenue
Settings:
  Check Refresh Status: true
  Expected Refresh: Every 1 hour
  Alert If Stale: > 2 hours
```

### BI Engine Monitoring

**Enterprise Plan Only**

Monitor BI Engine usage and performance:

```yaml
Monitor: BI Engine
Metrics:
  - Cache Hit Rate: > 80%
  - Cached Tables: List most accessed
  - Memory Usage: < 90%
```

---

## Best Practices

### 1. Use Service Accounts
More secure and auditable than OAuth for production environments.

### 2. Limit Permissions
Grant only necessary permissions (Data Viewer, not Editor).

### 3. Enable Query Cost Limits
Prevent runaway monitoring costs.

### 4. Leverage Partitioning
Always query partitioned tables with partition filters.

### 5. Monitor at Appropriate Intervals
- Real-time data: Every 5-15 minutes
- Batch data: Hourly or daily
- Large tables: Daily

### 6. Use Labels
Tag resources for better organization and cost attribution:

```yaml
Table Labels:
  environment: production
  team: data-engineering
  criticality: high
  monitored_by: datapulse
```

---

## Troubleshooting

### "Access Denied" Errors

**Issue**: DataPulse can't query tables

**Solutions**:
1. Verify service account has BigQuery Data Viewer role
2. Check dataset-level permissions
3. Ensure project ID is correct
4. Verify service account key hasn't expired

### High Query Costs

**Issue**: Monitoring is expensive

**Solutions**:
1. Enable sampling for large tables
2. Add partition filters
3. Reduce monitor frequency
4. Use cached query results
5. Review and optimize custom SQL monitors

### Slow Monitor Execution

**Issue**: Monitors take too long

**Solutions**:
1. Ensure tables are properly partitioned
2. Add clustering for frequently filtered columns
3. Use sampling for large tables
4. Split complex monitors into smaller ones
5. Schedule heavy monitors during off-peak hours

### Permission Issues After Rotation

**Issue**: Monitoring stops working after key rotation

**Solution**: Update service account key in DataPulse:
1. Generate new key in GCP
2. Go to DataPulse **Settings** > **Integrations** > **BigQuery**
3. Upload new key file
4. Test connection

---

## Security Best Practices

1. **Rotate Keys Regularly**: Every 90 days minimum
2. **Use Least Privilege**: Only grant necessary permissions
3. **Enable Audit Logging**: Track all BigQuery access
4. **Restrict IP Access**: Use VPC Service Controls (Enterprise)
5. **Monitor Service Account Usage**: Review logs for suspicious activity

---

## Example: Complete Setup for Production

```yaml
Setup:
  Authentication: Service Account
  Service Account: datapulse-prod@company.iam.gserviceaccount.com
  Permissions:
    - bigquery.dataViewer (dataset-level)
    - bigquery.jobUser (project-level)

Datasets Monitored:
  - production.analytics (15 tables)
  - production.events (8 tables)
  - production.user_data (5 tables)

Monitors:
  - Freshness: 12 monitors (15-min intervals)
  - Volume: 20 monitors (hourly)
  - Schema: 28 monitors (on-change)
  - Custom SQL: 8 monitors (daily)

Cost Controls:
  - Max query cost: $10/day
  - Sampling enabled: >1M rows
  - Off-peak scheduling: Large monitors

Alerts:
  - Critical: PagerDuty + Slack
  - High: Slack #data-alerts
  - Medium: Email digest
```

---

## Need Help?

- Email: support@datapulse.io
- Documentation: docs.datapulse.io/bigquery
- GCP Issues: See [Google Cloud Support](https://cloud.google.com/support)
