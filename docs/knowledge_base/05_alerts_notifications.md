# Alerts and Notifications

## Overview

DataPulse provides flexible alerting and notification options to ensure your team stays informed about data quality issues in real-time.

---

## Notification Channels

### 1. Email Notifications

**Available on**: All plans

Send alerts to individual email addresses or distribution lists.

**Configuration**:
```yaml
Channel: Email
Recipients:
  - data-team@company.com
  - oncall@company.com
Priority Levels:
  - Critical: Immediate
  - High: Within 5 minutes
  - Medium: Batched (every 30 min)
  - Low: Daily digest
```

**Features**:
- Rich HTML formatting with charts
- One-click incident acknowledgment
- Direct links to affected monitors
- Mobile-friendly design

---

### 2. Slack Integration

**Available on**: Pro and Enterprise plans

Send alerts directly to Slack channels.

**Setup**:
1. Go to **Settings** > **Integrations** > **Slack**
2. Click **Connect to Slack**
3. Authorize DataPulse
4. Select default channel (e.g., #data-alerts)
5. Configure per-monitor channels if needed

**Features**:
- Interactive buttons (Acknowledge, Snooze, View Details)
- Thread-based incident updates
- @mention specific users for critical alerts
- Rich formatting with monitor details
- Incident resolution notifications

**Example Slack Alert**:
```
🚨 CRITICAL: Freshness Monitor Failed
Monitor: orders_freshness_check
Table: production.orders
Issue: Data hasn't updated in 3 hours (threshold: 1 hour)
Last Update: 2024-01-15 14:32:00 UTC

[View Monitor] [Acknowledge] [Snooze 1h]
```

---

### 3. PagerDuty Integration

**Available on**: Pro and Enterprise plans

Route critical alerts to PagerDuty for on-call management.

**Setup**:
1. Generate a PagerDuty Integration Key
2. In DataPulse: **Settings** > **Integrations** > **PagerDuty**
3. Paste your Integration Key
4. Configure escalation policies

**Features**:
- Automatic incident creation
- Escalation policy support
- Incident acknowledgment sync
- Auto-resolution when monitors pass

**Routing Rules**:
```yaml
Rules:
  - If: severity == "critical"
    Then: Create PagerDuty incident (high urgency)
  - If: severity == "high" AND business_hours
    Then: Create PagerDuty incident (low urgency)
  - If: severity == "medium"
    Then: Email only
```

---

### 4. Webhook Notifications

**Available on**: Pro and Enterprise plans

Send alerts to custom webhooks for integration with your internal systems.

**Configuration**:
```json
{
  "webhook_url": "https://your-system.com/webhook",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
  },
  "retry_policy": {
    "max_retries": 3,
    "backoff": "exponential"
  }
}
```

**Payload Structure**:
```json
{
  "event_type": "monitor.failed",
  "timestamp": "2024-01-15T17:45:00Z",
  "severity": "critical",
  "monitor": {
    "id": "mon_12345",
    "name": "orders_freshness_check",
    "type": "freshness"
  },
  "resource": {
    "database": "production",
    "schema": "public",
    "table": "orders"
  },
  "details": {
    "expected": "< 1 hour",
    "actual": "3 hours 15 minutes",
    "last_update": "2024-01-15T14:30:00Z"
  },
  "incident_url": "https://app.datapulse.io/incidents/inc_67890"
}
```

---

### 5. Microsoft Teams

**Available on**: Pro and Enterprise plans

Send alerts to Microsoft Teams channels.

**Features**:
- Adaptive card formatting
- Action buttons for incident management
- Team member mentions
- Incident threading

---

### 6. SMS Notifications

**Available on**: Enterprise plan only

Send critical alerts via SMS for high-priority incidents.

**Configuration**:
- Verify phone numbers
- Set spending limits
- Define critical-only routing

---

## Alert Rules and Routing

### Severity Levels

DataPulse automatically assigns severity based on:

| Severity | Criteria | Color |
|----------|----------|-------|
| **Critical** | Production data, high-priority monitors, SLA breaches | 🔴 Red |
| **High** | Important tables, significant deviations | 🟠 Orange |
| **Medium** | Non-critical issues, minor anomalies | 🟡 Yellow |
| **Low** | Informational, schema changes (approved) | 🔵 Blue |

### Routing Configuration

**Simple Routing** (All Plans):
```yaml
Default Channel: Slack #data-quality
Override for Critical: PagerDuty + Email
```

**Advanced Routing** (Enterprise):
```yaml
Routes:
  - Name: Production Critical
    Conditions:
      - environment == "production"
      - severity >= "high"
    Channels:
      - PagerDuty (immediate)
      - Slack #production-alerts
      - SMS to oncall

  - Name: Staging Issues
    Conditions:
      - environment == "staging"
    Channels:
      - Slack #staging-alerts
      - Email to dev-team@company.com
    Schedule: Business hours only

  - Name: Data Team
    Conditions:
      - tags contains "data-quality"
    Channels:
      - Slack #data-team
    Batch: 15 minutes
```

---

## Alert Schedules

Control when alerts are sent:

### Business Hours
```yaml
Schedule:
  Type: Business Hours
  Timezone: America/New_York
  Days: Monday - Friday
  Hours: 9:00 AM - 5:00 PM
  Outside Hours: Suppress (except critical)
```

### Always On
```yaml
Schedule:
  Type: 24/7
  Timezone: UTC
```

### Custom Schedule
```yaml
Schedule:
  Type: Custom
  Include:
    - Mon-Fri: 8:00 AM - 10:00 PM EST
    - Sat: 9:00 AM - 6:00 PM EST
  Exclude:
    - Holidays: US Federal
    - Maintenance Windows: [specific dates]
```

---

## Alert Batching

Reduce alert fatigue by batching multiple alerts:

```yaml
Batching:
  Enabled: true
  Window: 15 minutes
  Max Alerts Per Batch: 10
  Group By:
    - Database
    - Table
    - Monitor Type
```

**Example Batched Alert**:
```
📊 5 Data Quality Issues Detected (Last 15 minutes)

Critical (2):
  - orders: Freshness threshold exceeded
  - payments: Volume anomaly detected

Medium (3):
  - users: Schema change detected
  - products: Null values increased
  - sessions: Distribution outlier

[View All Incidents]
```

---

## Alert Suppression

### Snooze Alerts
Temporarily suppress alerts for:
- Planned maintenance
- Known issues being worked on
- False positives under investigation

```yaml
Snooze Options:
  - 30 minutes
  - 1 hour
  - 4 hours
  - 24 hours
  - Custom duration
  - Until resolved
```

### Automatic Suppression Rules
```yaml
Suppression Rules:
  - Name: Weekend ETL Delay
    Condition: day_of_week in [Saturday, Sunday] AND monitor_type == "freshness"
    Duration: Until Monday 6 AM

  - Name: Known Issue #123
    Condition: table == "legacy_data"
    Duration: Until 2024-02-01
    Reason: "Legacy table being deprecated"
```

---

## Incident Management

### Auto-Acknowledgment
Automatically acknowledge incidents when:
- Monitor passes on next check
- Issue duration < threshold (flapping prevention)
- Related monitors also failing (grouped incident)

### Escalation Policies
```yaml
Escalation:
  Level 1: Data Engineer (on-call)
    Notify: Immediately
    Escalate After: 15 minutes

  Level 2: Data Team Lead
    Notify: If not acknowledged
    Escalate After: 30 minutes

  Level 3: Engineering Manager
    Notify: If still unresolved
```

---

## Alert Templates

Customize alert messages:

```jinja2
🚨 {{ severity | upper }}: {{ monitor.name }}

**Issue**: {{ issue_description }}
**Table**: {{ resource.table }}
**Threshold**: {{ threshold }}
**Actual**: {{ actual_value }}
**Duration**: {{ duration }}

**Impact**: {{ estimated_impact }}
**Runbook**: {{ runbook_url }}

[View Details]({{ incident_url }}) | [Acknowledge]({{ ack_url }})
```

---

## Testing Alerts

Test your notification channels:

1. Go to **Settings** > **Notifications**
2. Select a channel
3. Click **Send Test Alert**
4. Verify receipt

---

## Best Practices

1. **Start Broad, Then Refine**: Begin with email for all alerts, then add specific routing
2. **Use Severity Appropriately**: Not everything is critical - reserve for production SLA breaches
3. **Implement Batching**: Reduce noise during incident storms
4. **Document Runbooks**: Link to incident response procedures
5. **Review Alert Fatigue**: Monitor acknowledgment rates and adjust thresholds
6. **Test Regularly**: Ensure channels work during off-hours
7. **Maintain Oncall Rotations**: Keep PagerDuty schedules updated

---

## Troubleshooting

### Not Receiving Alerts?

1. Check notification channel configuration
2. Verify email/webhook is correct
3. Check spam folders
4. Review suppression rules
5. Check monitor schedule alignment

### Too Many Alerts?

1. Increase thresholds
2. Enable alert batching
3. Add business hours filtering
4. Review and remove redundant monitors
5. Use ML-based anomaly detection for better accuracy

---

## Need Help?

Contact support@datapulse.io or see [Monitor Types](./04_monitor_types.md) for setting up monitors.
