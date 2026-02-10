# Snowflake Integration Guide

## Overview

DataPulse provides native integration with Snowflake, allowing you to monitor data quality, track schema changes, and validate data freshness across all your Snowflake databases.

## Prerequisites

- Active Snowflake account
- ACCOUNTADMIN or SECURITYADMIN role (for initial setup)
- DataPulse Pro or Enterprise plan

## Setup Instructions

### Step 1: Create a DataPulse User in Snowflake

Run the following SQL in your Snowflake console:

```sql
-- Create user for DataPulse
CREATE USER datapulse_user
  PASSWORD = 'STRONG_PASSWORD_HERE'
  DEFAULT_ROLE = datapulse_role
  DEFAULT_WAREHOUSE = COMPUTE_WH;

-- Create role with read-only access
CREATE ROLE datapulse_role;

-- Grant necessary privileges
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE datapulse_role;
GRANT USAGE ON DATABASE YOUR_DATABASE TO ROLE datapulse_role;
GRANT USAGE ON ALL SCHEMAS IN DATABASE YOUR_DATABASE TO ROLE datapulse_role;
GRANT SELECT ON ALL TABLES IN DATABASE YOUR_DATABASE TO ROLE datapulse_role;
GRANT SELECT ON ALL VIEWS IN DATABASE YOUR_DATABASE TO ROLE datapulse_role;
GRANT SELECT ON FUTURE TABLES IN DATABASE YOUR_DATABASE TO ROLE datapulse_role;

-- Assign role to user
GRANT ROLE datapulse_role TO USER datapulse_user;
```

### Step 2: Configure Connection in DataPulse

1. Navigate to **Integrations** > **Add Integration**
2. Select **Snowflake**
3. Enter your connection details:
   - **Account Identifier**: `xy12345.us-east-1` (found in Snowflake URL)
   - **Username**: `datapulse_user`
   - **Password**: Your secure password
   - **Warehouse**: `COMPUTE_WH`
   - **Database**: Your database name
   - **Role**: `datapulse_role`

4. Click **Test Connection**
5. Once successful, click **Save Integration**

### Step 3: Select Tables to Monitor

1. After connecting, you'll see a list of available schemas and tables
2. Check the boxes next to tables you want to monitor
3. DataPulse will automatically:
   - Profile your data
   - Establish baseline metrics
   - Create default monitors for freshness and volume

## Advanced Configuration

### Using Key Pair Authentication (Recommended)

For enhanced security, use key pair authentication:

```sql
-- Generate key pair locally
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

-- Assign public key to user
ALTER USER datapulse_user SET RSA_PUBLIC_KEY='MIIBIjANBgkqhki...';
```

Then in DataPulse, select **Key Pair Authentication** and upload your private key.

### Monitoring Multiple Databases

To monitor multiple databases, repeat the GRANT commands for each database or use:

```sql
GRANT USAGE ON ALL DATABASES TO ROLE datapulse_role;
```

## Supported Features

- ✅ Table and view monitoring
- ✅ Schema change detection
- ✅ Data freshness checks
- ✅ Volume anomaly detection
- ✅ Custom SQL monitors
- ✅ Query performance analysis (Enterprise)
- ✅ Cost monitoring (Enterprise)

## Troubleshooting

### Connection Timeout

If you experience connection timeouts:
- Verify your Snowflake account identifier is correct
- Check network whitelisting (add DataPulse IPs: 52.1.2.3/32, 54.2.3.4/32)
- Ensure warehouse is running

### Permission Errors

If you see "Insufficient privileges" errors:
- Verify all GRANT statements were executed
- Check that the role is assigned to the user
- Ensure warehouse has credits available

## Performance Best Practices

1. **Use a dedicated warehouse**: Create a small warehouse specifically for DataPulse queries
2. **Limit scope**: Only grant access to databases/schemas you want to monitor
3. **Schedule monitors appropriately**: Avoid running monitors during peak hours

## Need Help?

Contact support@datapulse.io or chat with us in the app.
