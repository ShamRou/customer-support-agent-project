# AWS Redshift Integration Guide

## Overview

Connect DataPulse to Amazon Redshift to monitor your data warehouse with comprehensive data quality checks, performance monitoring, and anomaly detection.

## Prerequisites

- Active AWS account with Redshift cluster
- Admin access to Redshift cluster
- DataPulse Pro or Enterprise plan
- Network access (Security Group configuration)

---

## Quick Setup

### Step 1: Configure Security Group

Add DataPulse IP addresses to your Redshift security group:

**DataPulse IP Addresses**:
- `52.1.2.3/32`
- `54.2.3.4/32`

**AWS Console**:
1. Go to **EC2** > **Security Groups**
2. Find your Redshift security group
3. **Edit inbound rules**
4. Add rule:
   - Type: `Custom TCP`
   - Port: `5439` (or your custom port)
   - Source: `52.1.2.3/32`
5. Repeat for second IP
6. Save rules

**AWS CLI**:
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 5439 \
  --cidr 52.1.2.3/32

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 5439 \
  --cidr 54.2.3.4/32
```

---

### Step 2: Create DataPulse User

Create a dedicated read-only user for DataPulse:

```sql
-- Create user
CREATE USER datapulse_monitor WITH PASSWORD 'STRONG_PASSWORD_HERE';

-- Grant connect privilege
GRANT CONNECT ON DATABASE your_database TO datapulse_monitor;

-- Connect to your database
\c your_database

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO datapulse_monitor;
GRANT USAGE ON SCHEMA analytics TO datapulse_monitor;

-- Grant select on all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO datapulse_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO datapulse_monitor;

-- Grant select on future tables (important!)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO datapulse_monitor;

ALTER DEFAULT PRIVILEGES IN SCHEMA analytics
  GRANT SELECT ON TABLES TO datapulse_monitor;

-- Grant access to system tables (for metadata)
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO datapulse_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA information_schema TO datapulse_monitor;
```

---

### Step 3: Get Connection Details

Find your Redshift connection details:

**AWS Console**:
1. Go to **Amazon Redshift** > **Clusters**
2. Click your cluster name
3. Note down:
   - **Endpoint**: `cluster-name.abc123.us-east-1.redshift.amazonaws.com`
   - **Port**: `5439` (default)
   - **Database**: Your database name

**AWS CLI**:
```bash
aws redshift describe-clusters \
  --cluster-identifier your-cluster-name \
  --query 'Clusters[0].Endpoint'
```

---

### Step 4: Connect in DataPulse

1. Navigate to **Integrations** > **Add Integration**
2. Select **Amazon Redshift**
3. Enter connection details:
   - **Host**: `cluster-name.abc123.us-east-1.redshift.amazonaws.com`
   - **Port**: `5439`
   - **Database**: `your_database`
   - **Username**: `datapulse_monitor`
   - **Password**: Your secure password
   - **SSL Mode**: `require` (recommended)

4. Click **Test Connection**
5. Once successful, click **Save Integration**

---

### Step 5: Select Tables to Monitor

1. After connecting, you'll see available schemas and tables
2. Select tables you want to monitor
3. DataPulse will automatically:
   - Analyze table structure
   - Detect distribution keys
   - Establish baseline metrics
   - Create default monitors

---

## Advanced Configuration

### IAM Database Authentication

For enhanced security, use IAM authentication instead of passwords:

#### Step 1: Enable IAM Authentication

```bash
aws redshift modify-cluster \
  --cluster-identifier your-cluster-name \
  --iam-database-authentication-enabled
```

#### Step 2: Create IAM Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "redshift:GetClusterCredentials"
      ],
      "Resource": [
        "arn:aws:redshift:us-east-1:123456789012:dbuser:your-cluster/datapulse_monitor",
        "arn:aws:redshift:us-east-1:123456789012:dbname:your-cluster/your_database"
      ]
    }
  ]
}
```

#### Step 3: Create Database User

```sql
CREATE USER "IAMR:datapulse_role" WITH PASSWORD DISABLE;

GRANT CONNECT ON DATABASE your_database TO "IAMR:datapulse_role";
GRANT USAGE ON SCHEMA public TO "IAMR:datapulse_role";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "IAMR:datapulse_role";
```

#### Step 4: Configure in DataPulse

In DataPulse, select **IAM Authentication** and provide:
- IAM Role ARN
- AWS Access Key
- AWS Secret Key

---

## Monitoring Strategies

### Distribution Key Monitoring

Redshift uses distribution keys for performance. Monitor for skew:

```sql
-- Custom SQL Monitor: Check distribution skew
SELECT
  "table",
  MAX(size) * 100.0 / SUM(size) as max_skew_pct
FROM svv_table_info
WHERE "table" = 'your_table'
GROUP BY "table";

-- Alert if max_skew_pct > 10 (means one slice has >10% of data)
```

### Sort Key Monitoring

Ensure sort keys are effective:

```sql
-- Custom SQL Monitor: Check sort key effectiveness
SELECT
  "table",
  unsorted * 100.0 / rows as unsorted_pct
FROM svv_table_info
WHERE "table" = 'your_table';

-- Alert if unsorted_pct > 20 (needs VACUUM)
```

### Query Performance Monitoring

**Enterprise Plan Only**

Track slow queries and identify bottlenecks:

```yaml
Monitor Type: Query Performance
Thresholds:
  Duration: > 60 seconds
  Queue Time: > 30 seconds
  Rows Scanned: > 1 billion

Alert:
  Slack: #data-engineering
  Include: Query text, execution plan
```

---

## Redshift-Specific Monitors

### VACUUM Status

```sql
-- Custom Monitor: Tables needing VACUUM
SELECT
  tablename,
  unsorted * 100.0 / rows as unsorted_pct
FROM svv_table_info
WHERE schema = 'public'
  AND unsorted * 100.0 / rows > 20;

-- Alert if any tables returned
```

### ANALYZE Status

```sql
-- Custom Monitor: Tables needing ANALYZE
SELECT
  schemaname,
  tablename,
  DATEDIFF(day, last_stats_update, GETDATE()) as days_since_analyze
FROM svv_table_info
WHERE schema = 'public'
  AND DATEDIFF(day, last_stats_update, GETDATE()) > 7;

-- Alert if any tables returned
```

### Disk Space

```sql
-- Custom Monitor: Cluster disk usage
SELECT
  SUM(used) * 100.0 / SUM(capacity) as disk_used_pct
FROM stv_partitions;

-- Alert if disk_used_pct > 80
```

### Concurrency Issues

```sql
-- Custom Monitor: Query queue wait time
SELECT
  COUNT(*) as queued_queries
FROM stv_wlm_query_state
WHERE state = 'Queued';

-- Alert if queued_queries > 10
```

---

## Performance Best Practices

### 1. Use Appropriate Distribution Style

```yaml
Table Guidance:
  Small Tables (< 1M rows): DISTSTYLE ALL
  Medium Tables (1-10M): DISTKEY on join column
  Large Tables (> 10M): DISTKEY on frequently filtered column
  Very Large (> 100M): Consider EVEN distribution
```

### 2. Optimize Monitor Queries

```sql
-- ❌ Bad (no distribution key filter):
SELECT COUNT(*) FROM large_fact_table;

-- ✅ Good (uses distribution and sort keys):
SELECT COUNT(*) FROM large_fact_table
WHERE date >= CURRENT_DATE - 7  -- Sort key
  AND region = 'US-EAST';       -- Distribution key
```

### 3. Schedule Maintenance

```yaml
Recommended Schedule:
  VACUUM: Weekly (off-hours)
  ANALYZE: After large loads
  Monitor Frequency:
    - Small tables: Every 15 min
    - Large tables: Hourly or daily
```

### 4. Use Result Caching

DataPulse automatically uses Redshift's result cache when available:

```sql
-- Enable result caching
SET enable_result_cache_for_session TO true;
```

---

## Cost Optimization

### Monitor Query Costs

**Enterprise Plan Only**

Track query costs and optimize:

```yaml
Cost Monitor:
  Metrics:
    - Total query time
    - Disk spill events
    - Network traffic

  Alerts:
    - Daily cost > $X
    - Expensive queries (> 1 hour)
    - Disk spill (inefficient queries)
```

### Reduce Monitoring Costs

1. **Use WLM for DataPulse**:
   ```sql
   -- Create dedicated queue for monitoring
   -- With lower concurrency and priority
   ```

2. **Schedule Expensive Monitors Off-Peak**:
   ```yaml
   Large Table Monitors:
     Schedule: "0 2 * * *"  # 2 AM daily
   ```

3. **Enable Sampling**:
   ```yaml
   Monitor Settings:
     Sample Size: 10%
     Apply to Tables: > 100M rows
   ```

---

## Troubleshooting

### Connection Timeout

**Issue**: Cannot connect to Redshift

**Solutions**:
1. Verify security group rules (IPs whitelisted)
2. Check VPC routing (if using VPC)
3. Confirm cluster is available (not in maintenance)
4. Test from DataPulse's perspective:
   ```bash
   telnet cluster-name.region.redshift.amazonaws.com 5439
   ```

### Slow Monitor Execution

**Issue**: Monitors taking too long

**Solutions**:
1. Check if VACUUM/ANALYZE needed
2. Optimize monitor queries (use EXPLAIN)
3. Add appropriate filters (distribution/sort keys)
4. Enable sampling for large tables
5. Review WLM configuration

### Permission Errors

**Issue**: "Permission denied for table"

**Solutions**:
```sql
-- Check user grants
SELECT
  schemaname,
  tablename,
  has_table_privilege('datapulse_monitor',
                     schemaname||'.'||tablename,
                     'SELECT') as has_select
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema');

-- Re-grant if needed
GRANT SELECT ON ALL TABLES IN SCHEMA public TO datapulse_monitor;
```

### High Memory Usage

**Issue**: Monitoring queries causing high memory usage

**Solutions**:
1. Create dedicated WLM queue:
   ```sql
   -- Allocate 10% memory, low concurrency
   -- For datapulse_monitor user
   ```
2. Reduce monitor frequency
3. Add LIMIT to custom SQL monitors
4. Enable sampling

---

## Monitoring Redshift Spectrum

For external tables in S3:

```sql
-- Grant access to external schema
GRANT USAGE ON SCHEMA spectrum TO datapulse_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA spectrum TO datapulse_monitor;

-- Monitor external table freshness
SELECT
  tablename,
  MAX(last_altered) as last_altered
FROM svv_external_tables
WHERE schemaname = 'spectrum';
```

---

## Security Best Practices

1. **Use IAM Authentication** (recommended over passwords)
2. **Enable SSL** (set SSL Mode to 'require')
3. **Rotate Credentials** every 90 days
4. **Audit Access**:
   ```sql
   -- Check DataPulse user activity
   SELECT
     starttime,
     username,
     query
   FROM stl_query
   WHERE username = 'datapulse_monitor'
   ORDER BY starttime DESC
   LIMIT 100;
   ```

5. **Use VPC Endpoint** (Enterprise):
   - Private connection to Redshift
   - No internet exposure

---

## Migration from Legacy Redshift

If migrating from Redshift to RA3:

```yaml
Steps:
  1. Set up parallel monitoring on new cluster
  2. Compare baseline metrics
  3. Adjust distribution/sort keys if needed
  4. Update thresholds (RA3 may have different performance)
  5. Switch connections after validation
  6. Archive old cluster monitors
```

---

## Example: Complete Production Setup

```yaml
Setup:
  Cluster: production-redshift
  Instance Type: ra3.4xlarge (8 nodes)
  Authentication: IAM
  SSL: Required
  WLM: Dedicated queue for DataPulse (10% memory)

Schemas Monitored:
  - public (30 tables)
  - analytics (45 tables)
  - warehouse (20 tables)

Monitors:
  - Freshness: 15 monitors (15-min intervals)
  - Volume: 40 monitors (hourly)
  - Schema: 95 monitors (on-change)
  - Custom SQL: 12 monitors (daily)
  - Performance: 5 monitors (continuous)

Cost Controls:
  - Off-peak scheduling: Large monitors
  - Sampling: Tables > 100M rows
  - Result caching: Enabled
  - WLM optimization: Dedicated queue

Alerts:
  - Critical: PagerDuty + Slack
  - High: Slack #redshift-alerts
  - Medium: Email digest
```

---

## Resources

- AWS Redshift Documentation: aws.amazon.com/redshift/docs
- DataPulse Redshift Guide: docs.datapulse.io/redshift
- Performance Tuning: docs.datapulse.io/redshift/performance
- Support: support@datapulse.io

---

## Need Help?

- Redshift setup assistance: support@datapulse.io
- Performance optimization: success@datapulse.io
- AWS-specific questions: See AWS Support
