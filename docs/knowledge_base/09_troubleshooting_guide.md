# Troubleshooting Guide

## Overview

Common issues and their solutions for DataPulse users.

---

## Connection Issues

### Cannot Connect to Data Source

#### Snowflake Connection Timeout

**Symptoms**:
- "Connection timeout" error
- Can't test connection
- Integration status: "Disconnected"

**Solutions**:

1. **Verify Account Identifier**:
   ```
   Correct: xy12345.us-east-1
   Incorrect: xy12345 (missing region)
   Incorrect: xy12345.snowflakecomputing.com (don't include domain)
   ```

2. **Check Network Whitelisting**:
   Add DataPulse IPs to your Snowflake network policy:
   ```sql
   ALTER NETWORK POLICY datapulse_policy
   SET ALLOWED_IP_LIST = ('52.1.2.3/32', '54.2.3.4/32');
   ```

3. **Verify Warehouse is Running**:
   ```sql
   SHOW WAREHOUSES;
   -- Ensure your warehouse is in "STARTED" state
   ```

4. **Check User Permissions**:
   ```sql
   SHOW GRANTS TO USER datapulse_user;
   -- Should see USAGE on warehouse and database
   ```

#### BigQuery Authentication Failed

**Symptoms**:
- "403 Permission Denied" error
- "Invalid service account" message

**Solutions**:

1. **Verify Service Account Key**:
   - Ensure JSON key file is valid
   - Check key hasn't expired
   - Confirm correct project ID

2. **Check IAM Permissions**:
   Required roles:
   - `roles/bigquery.dataViewer`
   - `roles/bigquery.jobUser`
   - `roles/bigquery.metadataViewer`

3. **Enable BigQuery API**:
   ```bash
   gcloud services enable bigquery.googleapis.com
   ```

4. **Test from Command Line**:
   ```bash
   bq --project_id=YOUR_PROJECT ls
   # Should list datasets
   ```

---

## Monitor Issues

### Monitor Not Running

**Symptoms**:
- Monitor shows "Never run"
- No check history
- No alerts being sent

**Causes & Solutions**:

1. **Monitor is Paused**:
   - Go to Monitor > Resume

2. **Invalid Schedule**:
   - Check cron expression is valid
   - Use a cron validator: crontab.guru

3. **Data Source Disconnected**:
   - Check data source connection status
   - Reconnect if needed

4. **Table Not Found**:
   - Verify table still exists
   - Check if table was renamed
   - Update monitor configuration

### False Positive Alerts

**Symptoms**:
- Monitor fails but data looks correct
- Too many alerts for non-issues
- Alert fatigue

**Solutions**:

1. **Adjust Thresholds**:
   ```yaml
   # Before (too strict):
   Freshness: < 30 minutes

   # After (realistic):
   Freshness: < 2 hours
   ```

2. **Use Anomaly Detection** (Pro+):
   - Switch from static thresholds to ML-based detection
   - Set sensitivity: Low/Medium/High
   - Automatically adapts to patterns

3. **Add Business Hours Filter**:
   ```yaml
   Schedule:
     Type: Business Hours
     Days: Monday - Friday
     Hours: 9 AM - 5 PM
   ```

4. **Increase Grace Period**:
   ```yaml
   Config:
     Grace Period: 15 minutes
     Alert After: 2 consecutive failures
   ```

### Monitor Performance Issues

**Symptoms**:
- Monitor takes too long to run
- Query timeouts
- Expensive monitoring costs

**Solutions**:

1. **Enable Sampling** (for large tables):
   ```yaml
   Monitor Settings:
     Sampling: 10%
     Min Rows for Sampling: 1,000,000
   ```

2. **Optimize Custom SQL**:
   ```sql
   -- Before (full table scan):
   SELECT COUNT(*) FROM large_table WHERE status = 'active';

   -- After (with partition filter):
   SELECT COUNT(*) FROM large_table
   WHERE date_partition >= CURRENT_DATE - INTERVAL '7 days'
     AND status = 'active';
   ```

3. **Add Indexes**:
   ```sql
   CREATE INDEX idx_timestamp ON orders(created_at);
   ```

4. **Reduce Monitor Frequency**:
   ```
   Change from: Every 5 minutes
   To: Every 30 minutes
   ```

---

## Alert & Notification Issues

### Not Receiving Email Alerts

**Symptoms**:
- Monitors failing but no emails received
- Missing critical alerts

**Solutions**:

1. **Check Spam Folder**:
   - Add noreply@datapulse.io to contacts
   - Whitelist domain: *.datapulse.io

2. **Verify Email Address**:
   - Settings > Notifications > Email
   - Ensure email is verified (check for verification link)

3. **Check Alert Rules**:
   - Settings > Notifications > Routing
   - Verify severity routing includes email

4. **Test Email Delivery**:
   - Settings > Notifications > Email > Send Test

### Slack Alerts Not Working

**Symptoms**:
- Slack integration shows "Connected"
- But no messages appearing in channel

**Solutions**:

1. **Re-authorize Slack**:
   - Settings > Integrations > Slack > Reconnect
   - Grant all required permissions

2. **Check Channel Selection**:
   - Verify correct channel selected
   - Ensure DataPulse bot is in channel:
     ```
     /invite @DataPulse
     ```

3. **Check Slack Workspace Permissions**:
   - Admin may have restricted app installations
   - Contact Slack workspace admin

4. **Test Slack Integration**:
   - Settings > Integrations > Slack > Send Test Message

### Too Many Alerts (Alert Fatigue)

**Symptoms**:
- Hundreds of alerts per day
- Team ignoring alerts
- Low acknowledgment rate

**Solutions**:

1. **Enable Alert Batching**:
   ```yaml
   Batching:
     Enabled: true
     Window: 15 minutes
     Group By: [table, severity]
   ```

2. **Use Smart Suppression** (Enterprise):
   ```yaml
   Suppression:
     Auto-suppress downstream: true
     Only alert on root cause: true
   ```

3. **Adjust Severity Levels**:
   ```yaml
   # Not everything is critical
   Critical: Production SLA breaches only
   High: Important but not urgent
   Medium: Minor issues
   Low: Informational
   ```

4. **Review and Tune Monitors**:
   - Weekly: Review alert volume
   - Monthly: Adjust thresholds
   - Quarterly: Archive unused monitors

---

## Data Quality Issues

### Data Shows as Stale But It's Current

**Symptoms**:
- Freshness monitor fails
- But data is actually recent

**Solutions**:

1. **Check Timestamp Column**:
   ```sql
   -- Verify you're using the right column
   SELECT MAX(created_at) FROM orders;
   SELECT MAX(updated_at) FROM orders;
   ```

2. **Timezone Issues**:
   ```yaml
   # Specify timezone in monitor:
   Config:
     Timestamp Column: created_at
     Timezone: America/New_York
   ```

3. **Check for NULL Timestamps**:
   ```sql
   SELECT COUNT(*) FROM orders WHERE created_at IS NULL;
   -- If many NULLs, use WHERE created_at IS NOT NULL in monitor
   ```

### Volume Anomalies Every Weekend

**Symptoms**:
- Volume monitor fails every Saturday/Sunday
- Data is actually correct (just lower volume)

**Solutions**:

1. **Use ML Anomaly Detection** (Pro+):
   - Automatically learns weekly patterns
   - Accounts for weekends, holidays

2. **Set Day-of-Week Thresholds**:
   ```yaml
   Config:
     Weekday Threshold: 90,000 - 110,000
     Weekend Threshold: 10,000 - 30,000
   ```

3. **Disable on Weekends**:
   ```yaml
   Schedule:
     Days: Monday - Friday only
   ```

### Schema Changes Not Detected

**Symptoms**:
- Column added but no alert
- Schema monitor shows no changes

**Solutions**:

1. **Check Monitor Status**:
   - Ensure schema monitor is active
   - Verify last run time

2. **Force Metadata Refresh**:
   - Data Sources > Your Source > Sync Metadata

3. **Check Schema Cache**:
   - Monitor > Schema > View History
   - Last cached schema should be recent

---

## Performance Issues

### Dashboard Loading Slowly

**Symptoms**:
- DataPulse dashboard takes >10 seconds to load
- Timeout errors

**Solutions**:

1. **Reduce Date Range**:
   - Default view: Last 7 days
   - Use filters for longer ranges

2. **Clear Browser Cache**:
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

3. **Check Browser Console**:
   - F12 > Console
   - Look for errors
   - Report to support if found

4. **Try Incognito Mode**:
   - Rules out extension conflicts

### Lineage Graph Won't Load

**Symptoms**:
- Lineage visualization stuck loading
- Blank lineage page

**Solutions**:

1. **Reduce Lineage Depth**:
   ```
   Change from: 5 levels upstream/downstream
   To: 2 levels upstream/downstream
   ```

2. **Filter by Type**:
   - Hide external tables
   - Show only tables (not views)

3. **Search Instead**:
   - Use search bar to jump to specific table
   - View focused subgraph

---

## API Issues

### API Rate Limit Exceeded

**Symptoms**:
- 429 HTTP status code
- "Rate limit exceeded" error

**Solutions**:

1. **Implement Backoff**:
   ```python
   import time
   from datapulse import Client, RateLimitError

   client = Client(api_key="...")

   for attempt in range(3):
       try:
           result = client.monitors.list()
           break
       except RateLimitError:
           wait_time = 2 ** attempt  # Exponential backoff
           time.sleep(wait_time)
   ```

2. **Check Rate Limit Headers**:
   ```python
   response = client.monitors.list()
   print(f"Remaining: {response.rate_limit_remaining}")
   print(f"Reset: {response.rate_limit_reset}")
   ```

3. **Upgrade Plan** (if Pro):
   - Enterprise has unlimited API requests

4. **Cache Results**:
   ```python
   # Cache monitor list for 5 minutes
   from functools import lru_cache
   import time

   @lru_cache(maxsize=1)
   def get_monitors():
       return client.monitors.list()
   ```

### API Authentication Failed

**Symptoms**:
- 401 HTTP status code
- "Invalid API key" error

**Solutions**:

1. **Verify API Key**:
   - Check for typos
   - Ensure no trailing spaces
   - Key format: `dp_xxx...`

2. **Check Key Status**:
   - Settings > API Keys
   - Ensure key is active (not revoked)

3. **Verify Permissions**:
   - Read-only key can't create monitors
   - Use appropriate key type

4. **Regenerate Key**:
   - If compromised, regenerate immediately

---

## Data Source Specific Issues

### Snowflake: High Query Costs

**Symptoms**:
- Unexpected Snowflake bills
- Many queries from DataPulse

**Solutions**:

1. **Use Dedicated Small Warehouse**:
   ```sql
   CREATE WAREHOUSE datapulse_wh
   WITH WAREHOUSE_SIZE = 'XSMALL'
   AUTO_SUSPEND = 60;
   ```

2. **Enable Query Result Caching**:
   ```sql
   ALTER WAREHOUSE datapulse_wh
   SET USE_CACHED_RESULT = TRUE;
   ```

3. **Review Monitor Schedule**:
   - Reduce frequency for non-critical monitors
   - Run expensive monitors daily vs. hourly

4. **Enable Sampling** in DataPulse:
   ```yaml
   Monitor Settings:
     Sample Large Tables: true
     Sample Size: 10%
   ```

### BigQuery: Permission Errors After Project Changes

**Symptoms**:
- Monitors suddenly failing
- "Permission denied" errors
- Worked fine yesterday

**Solutions**:

1. **Check Recent IAM Changes**:
   - GCP Console > IAM & Admin > Audit Logs
   - Look for permission removals

2. **Re-grant Permissions**:
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:datapulse@project.iam.gserviceaccount.com" \
     --role="roles/bigquery.dataViewer"
   ```

3. **Check Organization Policies**:
   - Org-level policies may override project permissions

---

## Getting Help

### Before Contacting Support

1. **Check Status Page**: status.datapulse.io
2. **Search Documentation**: docs.datapulse.io
3. **Check Community**: community.datapulse.io
4. **Review Audit Logs**: Settings > Audit Logs

### What to Include in Support Requests

```
Subject: [Brief description of issue]

Environment:
- DataPulse Plan: Pro/Enterprise
- Data Source Type: Snowflake/BigQuery/etc.
- Browser (if UI issue): Chrome 120

Issue Description:
- What happened: [detailed description]
- Expected behavior: [what should happen]
- When it started: [date/time]
- Frequency: Always/Sometimes/Once

Steps to Reproduce:
1. Go to...
2. Click on...
3. See error...

Error Messages:
[Paste exact error messages]

Screenshots:
[Attach screenshots if applicable]

Monitor/Incident ID (if applicable):
mon_abc123, inc_xyz789
```

### Support Channels

| Plan | Email | Chat | Phone | Response Time |
|------|-------|------|-------|---------------|
| Free | ❌ | ❌ | ❌ | Community only |
| Pro | ✅ | ✅ (9-5 EST) | ❌ | < 24 hours |
| Enterprise | ✅ | ✅ (24/7) | ✅ | < 4 hours |

**Contact**:
- Email: support@datapulse.io
- Chat: In-app (bottom right corner)
- Community: community.datapulse.io
- Status: status.datapulse.io

---

## Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `Table not found` | Table doesn't exist or no access | Verify table name and permissions |
| `Invalid cron expression` | Monitor schedule invalid | Use crontab.guru to validate |
| `Query timeout` | Query took too long | Optimize query or increase timeout |
| `Insufficient permissions` | Missing required access | Grant necessary permissions |
| `Rate limit exceeded` | Too many API requests | Implement backoff, upgrade plan |
| `Invalid timestamp column` | Column doesn't exist or wrong type | Check column name and data type |
| `Connection reset` | Network issue | Check firewall, retry |
| `Invalid API key` | Key revoked or incorrect | Regenerate API key |

---

## Still Need Help?

If you couldn't find a solution:
1. Email: support@datapulse.io
2. Include monitor/incident ID
3. Attach screenshots
4. Describe what you've tried

Our team typically responds within 24 hours (Pro) or 4 hours (Enterprise).
