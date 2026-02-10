# Getting Started with DataPulse

## Welcome to DataPulse

DataPulse is a comprehensive data observability platform that helps you monitor, validate, and ensure the quality of your data pipelines in real-time.

## Quick Start Guide

### Step 1: Create Your Account

1. Visit [app.datapulse.io](https://app.datapulse.io)
2. Sign up with your email or use SSO (Enterprise only)
3. Verify your email address
4. Complete the onboarding wizard

### Step 2: Connect Your First Data Source

DataPulse supports multiple data sources:
- **Data Warehouses**: Snowflake, BigQuery, Redshift, Databricks
- **Databases**: PostgreSQL, MySQL, MongoDB
- **Data Lakes**: S3, Azure Data Lake, GCS
- **Streaming**: Kafka, Kinesis

To connect a data source:
1. Navigate to **Integrations** in the left sidebar
2. Click **Add Integration**
3. Select your data source type
4. Enter connection credentials
5. Test the connection
6. Save and activate

### Step 3: Set Up Your First Monitor

Monitors automatically check your data quality:

1. Go to **Monitors** > **Create Monitor**
2. Choose a monitor type:
   - **Freshness**: Ensures data is up-to-date
   - **Volume**: Detects anomalies in row counts
   - **Schema**: Tracks schema changes
   - **Custom SQL**: Write custom validation queries
3. Configure thresholds and schedule
4. Set up notifications (email, Slack, PagerDuty)

### Step 4: View Your Data Health Dashboard

Your dashboard provides:
- Real-time data quality scores
- Active incidents and alerts
- Data lineage visualization
- Historical trends and patterns

## Next Steps

- [Connect to Snowflake](./02_snowflake_integration.md)
- [Set up Custom Alerts](./05_alerts_notifications.md)
- [Explore API Documentation](./08_api_documentation.md)

## Need Help?

- Email: support@datapulse.io
- Live Chat: Available 9am-5pm EST (Pro & Enterprise)
- Documentation: docs.datapulse.io
