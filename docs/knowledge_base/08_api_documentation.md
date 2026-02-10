# API Documentation

## Overview

The DataPulse API allows you to programmatically manage monitors, query incidents, access lineage data, and integrate DataPulse into your workflows.

**Available on**: Pro and Enterprise plans

**Base URL**: `https://api.datapulse.io/v1`

---

## Authentication

### API Keys

Generate API keys in **Settings** > **API Keys**.

**Key Types**:
- **Read-only**: Query data, list resources
- **Read-write**: Create/update monitors, acknowledge incidents
- **Admin**: Full access including user management (Enterprise only)

### Authentication Methods

#### Bearer Token (Recommended)
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.datapulse.io/v1/monitors
```

#### API Key Header
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  https://api.datapulse.io/v1/monitors
```

---

## Rate Limits

| Plan | Requests/Hour | Burst |
|------|--------------|-------|
| Pro | 10,000 | 100/min |
| Enterprise | Unlimited | 1000/min |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9547
X-RateLimit-Reset: 1640000000
```

---

## Endpoints

### Monitors

#### List Monitors
```http
GET /monitors
```

**Query Parameters**:
- `status`: `active`, `paused`, `disabled`
- `type`: `freshness`, `volume`, `schema`, `custom_sql`
- `table`: Filter by table name
- `page`: Page number (default: 1)
- `limit`: Results per page (max: 100)

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.datapulse.io/v1/monitors?type=freshness&status=active"
```

**Response**:
```json
{
  "data": [
    {
      "id": "mon_abc123",
      "name": "orders_freshness_check",
      "type": "freshness",
      "status": "active",
      "table": {
        "database": "production",
        "schema": "public",
        "name": "orders"
      },
      "config": {
        "timestamp_column": "created_at",
        "threshold": "1 hour",
        "schedule": "*/15 * * * *"
      },
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-20T15:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1,
    "pages": 1
  }
}
```

#### Get Monitor
```http
GET /monitors/:id
```

#### Create Monitor
```http
POST /monitors
```

**Request Body**:
```json
{
  "name": "payments_volume_check",
  "type": "volume",
  "table": {
    "database": "production",
    "schema": "public",
    "name": "payments"
  },
  "config": {
    "comparison": "day_over_day",
    "threshold": {
      "min": 90000,
      "max": 110000
    },
    "schedule": "0 * * * *"
  },
  "notifications": {
    "channels": ["slack", "email"],
    "severity": "high"
  }
}
```

**Response**:
```json
{
  "id": "mon_xyz789",
  "status": "active",
  "message": "Monitor created successfully"
}
```

#### Update Monitor
```http
PUT /monitors/:id
PATCH /monitors/:id
```

#### Delete Monitor
```http
DELETE /monitors/:id
```

#### Pause/Resume Monitor
```http
POST /monitors/:id/pause
POST /monitors/:id/resume
```

---

### Incidents

#### List Incidents
```http
GET /incidents
```

**Query Parameters**:
- `status`: `open`, `acknowledged`, `resolved`
- `severity`: `critical`, `high`, `medium`, `low`
- `monitor_id`: Filter by monitor
- `from`: Start date (ISO 8601)
- `to`: End date (ISO 8601)

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.datapulse.io/v1/incidents?status=open&severity=critical"
```

**Response**:
```json
{
  "data": [
    {
      "id": "inc_def456",
      "monitor_id": "mon_abc123",
      "monitor_name": "orders_freshness_check",
      "status": "open",
      "severity": "critical",
      "detected_at": "2024-01-20T14:30:00Z",
      "details": {
        "expected": "< 1 hour",
        "actual": "3 hours 15 minutes",
        "last_update": "2024-01-20T11:15:00Z"
      },
      "table": {
        "database": "production",
        "schema": "public",
        "name": "orders"
      },
      "impact": {
        "downstream_tables": 5,
        "dashboards": 2,
        "estimated_users": 45
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1,
    "pages": 1
  }
}
```

#### Get Incident
```http
GET /incidents/:id
```

#### Acknowledge Incident
```http
POST /incidents/:id/acknowledge
```

**Request Body**:
```json
{
  "acknowledged_by": "jane@company.com",
  "notes": "Investigating ETL job failure"
}
```

#### Resolve Incident
```http
POST /incidents/:id/resolve
```

**Request Body**:
```json
{
  "resolved_by": "jane@company.com",
  "resolution": "ETL job restarted, data now fresh",
  "root_cause": "Database connection timeout"
}
```

#### Add Comment
```http
POST /incidents/:id/comments
```

---

### Data Sources

#### List Data Sources
```http
GET /datasources
```

**Response**:
```json
{
  "data": [
    {
      "id": "ds_snowflake_prod",
      "name": "Production Snowflake",
      "type": "snowflake",
      "status": "connected",
      "config": {
        "account": "xy12345.us-east-1",
        "warehouse": "COMPUTE_WH",
        "database": "PRODUCTION"
      },
      "statistics": {
        "tables_monitored": 45,
        "monitors_active": 120,
        "last_sync": "2024-01-20T15:00:00Z"
      }
    }
  ]
}
```

#### Test Connection
```http
POST /datasources/:id/test
```

#### Sync Metadata
```http
POST /datasources/:id/sync
```

Forces a metadata refresh for the data source.

---

### Lineage (Enterprise)

#### Get Upstream Dependencies
```http
GET /lineage/:table/upstream
```

**Query Parameters**:
- `levels`: Number of levels (default: 3, max: 10)
- `include_columns`: Include column-level lineage (boolean)

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.datapulse.io/v1/lineage/production.public.fact_orders/upstream?levels=2"
```

**Response**:
```json
{
  "table": "production.public.fact_orders",
  "upstream": [
    {
      "table": "production.public.raw_orders",
      "level": 1,
      "relationship": "direct",
      "last_updated": "2024-01-20T14:00:00Z"
    },
    {
      "table": "production.public.raw_customers",
      "level": 1,
      "relationship": "direct",
      "last_updated": "2024-01-20T14:00:00Z"
    }
  ]
}
```

#### Get Downstream Consumers
```http
GET /lineage/:table/downstream
```

#### Impact Analysis
```http
POST /lineage/:table/impact
```

**Request Body**:
```json
{
  "scenario": "data_loss",
  "include_dashboards": true,
  "include_ml_models": true
}
```

**Response**:
```json
{
  "table": "production.public.raw_orders",
  "impact": {
    "affected_tables": 8,
    "broken_dashboards": 3,
    "failed_ml_models": 1,
    "estimated_users": 150,
    "criticality": "high"
  },
  "details": {
    "tables": [
      {
        "name": "fact_orders",
        "severity": "critical",
        "time_to_impact": "30 minutes"
      }
    ],
    "dashboards": [
      {
        "name": "Executive Revenue Dashboard",
        "users": 45,
        "severity": "critical"
      }
    ]
  }
}
```

---

### Metrics & Analytics

#### Get Data Quality Score
```http
GET /metrics/quality-score
```

**Query Parameters**:
- `table`: Specific table (optional)
- `from`: Start date
- `to`: End date
- `granularity`: `hour`, `day`, `week`, `month`

**Response**:
```json
{
  "overall_score": 94.5,
  "period": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-20T23:59:59Z"
  },
  "breakdown": {
    "freshness": 96.2,
    "volume": 93.5,
    "schema": 98.1,
    "custom": 91.8
  },
  "trend": "improving",
  "timeseries": [
    {
      "timestamp": "2024-01-20T00:00:00Z",
      "score": 94.5
    }
  ]
}
```

#### Get Incident Statistics
```http
GET /metrics/incidents
```

**Response**:
```json
{
  "period": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-20T23:59:59Z"
  },
  "total_incidents": 45,
  "by_severity": {
    "critical": 5,
    "high": 15,
    "medium": 20,
    "low": 5
  },
  "mttr": "2h 15m",
  "mttd": "12m",
  "resolved": 42,
  "open": 3
}
```

---

## Webhooks

### Configure Webhooks

```http
POST /webhooks
```

**Request Body**:
```json
{
  "url": "https://your-system.com/webhook",
  "events": [
    "monitor.failed",
    "monitor.recovered",
    "incident.created",
    "incident.resolved"
  ],
  "secret": "your_webhook_secret",
  "active": true
}
```

### Webhook Events

#### monitor.failed
```json
{
  "event": "monitor.failed",
  "timestamp": "2024-01-20T14:30:00Z",
  "data": {
    "monitor_id": "mon_abc123",
    "monitor_name": "orders_freshness_check",
    "severity": "critical",
    "table": "production.public.orders",
    "details": {
      "expected": "< 1 hour",
      "actual": "3 hours"
    }
  }
}
```

### Verify Webhook Signatures

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

---

## SDKs

### Python
```bash
pip install datapulse
```

```python
from datapulse import Client

client = Client(api_key="your_api_key")

# List monitors
monitors = client.monitors.list(status="active")

# Create monitor
monitor = client.monitors.create(
    name="orders_volume_check",
    type="volume",
    table="production.public.orders",
    config={
        "threshold": {"min": 90000, "max": 110000},
        "schedule": "0 * * * *"
    }
)

# Get incidents
incidents = client.incidents.list(status="open", severity="critical")

# Acknowledge incident
client.incidents.acknowledge(
    incident_id="inc_def456",
    notes="Investigating"
)
```

### JavaScript/TypeScript
```bash
npm install @datapulse/sdk
```

```typescript
import { DataPulseClient } from '@datapulse/sdk';

const client = new DataPulseClient({
  apiKey: 'your_api_key'
});

// List monitors
const monitors = await client.monitors.list({ status: 'active' });

// Create monitor
const monitor = await client.monitors.create({
  name: 'orders_volume_check',
  type: 'volume',
  table: 'production.public.orders',
  config: {
    threshold: { min: 90000, max: 110000 },
    schedule: '0 * * * *'
  }
});
```

---

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Monitor type 'invalid_type' is not supported",
    "details": {
      "field": "type",
      "allowed_values": ["freshness", "volume", "schema", "custom_sql"]
    }
  },
  "request_id": "req_abc123"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_request` | 400 | Invalid request parameters |
| `authentication_failed` | 401 | Invalid or missing API key |
| `permission_denied` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Too many requests |
| `internal_error` | 500 | Server error |

---

## Best Practices

1. **Use Read-only Keys**: For read-only operations, use read-only API keys
2. **Handle Rate Limits**: Implement exponential backoff
3. **Verify Webhooks**: Always verify webhook signatures
4. **Cache Responses**: Cache monitor lists and metadata
5. **Use Pagination**: Don't fetch all results at once
6. **Monitor API Usage**: Track your API usage in Settings
7. **Test in Sandbox**: Use test API keys for development

---

## Need Help?

- Full API Reference: docs.datapulse.io/api
- SDK Documentation: docs.datapulse.io/sdks
- Support: api-support@datapulse.io
