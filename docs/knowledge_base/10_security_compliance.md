# Security & Compliance

## Overview

DataPulse takes security and compliance seriously. This document outlines our security practices, compliance certifications, and features to help you meet your organization's requirements.

---

## Security Architecture

### Data Encryption

#### In Transit
- **TLS 1.3**: All data transmission uses TLS 1.3
- **Certificate Pinning**: Mobile and desktop apps use certificate pinning
- **Perfect Forward Secrecy**: Enabled on all connections

#### At Rest
- **AES-256 Encryption**: All data encrypted using AES-256
- **Encrypted Backups**: Automatic encrypted backups every 6 hours
- **Key Management**: AWS KMS (Enterprise: Bring Your Own Key supported)

### Network Security

```
Internet
    ↓
[CloudFlare WAF]
    ↓
[AWS Application Load Balancer]
    ↓
[DataPulse Application Layer]
    ↓
[Encrypted Database - RDS]
```

**Features**:
- DDoS protection via CloudFlare
- Web Application Firewall (WAF)
- IP whitelisting (Enterprise)
- VPC peering (Enterprise)
- Private endpoints (Enterprise)

---

## Authentication & Access Control

### Single Sign-On (SSO)

**Available on**: Enterprise plan

**Supported Protocols**:
- SAML 2.0
- OAuth 2.0
- OpenID Connect (OIDC)

**Supported Providers**:
- Okta
- Azure AD
- Google Workspace
- OneLogin
- Auth0
- Custom SAML providers

**Setup**:
```yaml
SSO Configuration:
  Provider: Okta
  Entity ID: https://company.okta.com
  SSO URL: https://company.okta.com/app/datapulse/sso
  Certificate: [Upload X.509 certificate]

Settings:
  Just-in-Time Provisioning: Enabled
  Default Role: Viewer
  Require SSO: true
```

### Multi-Factor Authentication (MFA)

**Available on**: All plans

**Supported Methods**:
- Authenticator apps (Google Authenticator, Authy)
- SMS (optional)
- Hardware tokens (YubiKey - Enterprise)
- Biometric (WebAuthn - Enterprise)

**Enforcement**:
```yaml
MFA Policy:
  Required for: All users
  Grace Period: 7 days
  Backup Codes: 10 generated
  Recovery: Admin approval required
```

### Role-Based Access Control (RBAC)

**Available on**: Pro (basic), Enterprise (advanced)

#### Default Roles

| Role | Permissions |
|------|-------------|
| **Viewer** | View monitors, incidents, dashboards |
| **Editor** | Create/edit monitors, acknowledge incidents |
| **Admin** | Full access, manage users, billing |
| **Auditor** | Read-only access to everything including audit logs |

#### Custom Roles (Enterprise)

```yaml
Role: Data Engineer
Permissions:
  Monitors:
    - Create: true
    - Edit: true
    - Delete: true
  Incidents:
    - View: true
    - Acknowledge: true
    - Resolve: true
  Integrations:
    - View: true
    - Edit: false
  Settings:
    - View: false
    - Edit: false

Scope:
  Databases: [production, staging]
  Exclude: [pii_database]
```

---

## Data Privacy

### Data Handling

**What DataPulse Stores**:
- ✅ Table/column metadata (names, types, sizes)
- ✅ Data quality metrics (row counts, null rates)
- ✅ Query results from monitors (aggregated only)
- ✅ Audit logs (who did what, when)

**What DataPulse NEVER Stores**:
- ❌ Raw table data (except monitor query results)
- ❌ Customer PII (unless in monitor queries)
- ❌ Database passwords (encrypted in transit, hashed at rest)
- ❌ Query results from your analytics tools

### Data Residency (Enterprise)

Choose where your data is stored:

**Available Regions**:
- 🇺🇸 US East (N. Virginia) - us-east-1
- 🇺🇸 US West (Oregon) - us-west-2
- 🇪🇺 EU (Frankfurt) - eu-central-1
- 🇪🇺 EU (Ireland) - eu-west-1
- 🇬🇧 UK (London) - eu-west-2
- 🇨🇦 Canada (Montreal) - ca-central-1
- 🇦🇺 Asia Pacific (Sydney) - ap-southeast-2

### Data Retention

| Data Type | Free | Pro | Enterprise |
|-----------|------|-----|------------|
| Monitor Results | 7 days | 90 days | 1 year+ |
| Incidents | 30 days | 1 year | Unlimited |
| Audit Logs | 30 days | 1 year | 7 years |
| Metrics | 30 days | 90 days | 1 year+ |

### Data Deletion

**Right to Delete**:
- Request data deletion anytime
- Complete deletion within 30 days
- Backup deletion within 90 days

**Account Deletion**:
```
Settings > Account > Delete Account
↓
Confirm deletion
↓
All data queued for deletion
↓
Email confirmation
↓
Data purged within 30 days
```

---

## Compliance Certifications

### SOC 2 Type II

**Status**: ✅ Certified

**Audit Period**: Annual

**Scope**: Security, Availability, Confidentiality

**Report**: Available to Enterprise customers via NDA

### GDPR Compliance

**Status**: ✅ Compliant

**Features**:
- Data Processing Agreement (DPA) available
- EU data residency option
- Right to access, rectify, delete data
- Data portability
- Privacy by design

**DPA**:
```
Available at: legal.datapulse.io/dpa
Sign online or via DocuSign
Standard Contractual Clauses included
```

### HIPAA (Enterprise)

**Status**: ✅ Available via BAA

**Features**:
- Business Associate Agreement (BAA)
- PHI encryption at rest and in transit
- Audit logging
- Access controls
- Incident response

**Contact**: hipaa@datapulse.io for BAA

### ISO 27001

**Status**: 🔄 In Progress (Expected Q2 2024)

### PCI DSS

**Note**: DataPulse does not process payment card data. Your payment information is processed by Stripe (PCI DSS Level 1 certified).

---

## Audit Logging

**Available on**: Pro (basic), Enterprise (advanced)

### Logged Events

```yaml
User Actions:
  - Login attempts (success/failure)
  - Logout
  - Password changes
  - MFA setup/removal

Monitor Actions:
  - Monitor created/updated/deleted
  - Monitor paused/resumed
  - Monitor configuration changes

Data Source Actions:
  - Integration added/removed
  - Connection test performed
  - Credentials updated

Incident Actions:
  - Incident created
  - Incident acknowledged
  - Incident resolved
  - Comment added

Admin Actions:
  - User invited/removed
  - Role assigned/changed
  - Settings modified
  - API key created/revoked
```

### Audit Log Format

```json
{
  "timestamp": "2024-01-20T15:30:00Z",
  "event_type": "monitor.created",
  "actor": {
    "user_id": "usr_abc123",
    "email": "jane@company.com",
    "ip_address": "203.0.113.42",
    "user_agent": "Mozilla/5.0..."
  },
  "resource": {
    "type": "monitor",
    "id": "mon_xyz789",
    "name": "orders_freshness_check"
  },
  "changes": {
    "name": "orders_freshness_check",
    "type": "freshness",
    "threshold": "1 hour"
  },
  "result": "success"
}
```

### Audit Log Export

```bash
# Export via API (Enterprise)
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.datapulse.io/v1/audit-logs?from=2024-01-01&to=2024-01-31" \
  > audit-logs-jan-2024.json

# Export via UI
Settings > Audit Logs > Export > [Date Range] > CSV/JSON
```

---

## Vulnerability Management

### Security Testing

- **Penetration Testing**: Annual third-party pen tests
- **Vulnerability Scanning**: Weekly automated scans
- **Dependency Scanning**: Daily checks for vulnerable libraries
- **Static Analysis**: Every code commit
- **Dynamic Analysis**: Pre-production testing

### Responsible Disclosure

**Report Security Issues**:
- Email: security@datapulse.io
- PGP Key: Available at security.datapulse.io/pgp
- Bug Bounty: Available for qualifying issues

**Response SLA**:
- Acknowledgment: Within 24 hours
- Assessment: Within 72 hours
- Fix: Based on severity
  - Critical: 7 days
  - High: 30 days
  - Medium: 90 days

---

## Incident Response

### Security Incident Process

```
Incident Detected
    ↓
[Assess Severity]
    ↓
[Contain Threat]
    ↓
[Investigate Root Cause]
    ↓
[Remediate]
    ↓
[Notify Affected Customers]
    ↓
[Post-Mortem & Improvements]
```

### Customer Notification

**We notify customers within 72 hours if**:
- Unauthorized access to customer data
- Data breach affecting PII
- Service compromise affecting security

### Incident Response Team

- Security Engineer (24/7 on-call)
- CTO
- VP Engineering
- Legal Counsel (if needed)

---

## Best Practices for Customers

### 1. Use Service Accounts (not personal credentials)

```sql
-- Create dedicated user for DataPulse
CREATE USER datapulse_monitor WITH PASSWORD '...';

-- Don't use personal admin accounts
❌ CREATE USER john.doe_admin WITH PASSWORD '...';
```

### 2. Principle of Least Privilege

```yaml
# Grant only necessary permissions
✅ GRANT SELECT ON database.schema.* TO datapulse_monitor;

# Don't grant excessive permissions
❌ GRANT ALL PRIVILEGES ON *.* TO datapulse_monitor;
```

### 3. Rotate Credentials Regularly

```
Recommended Rotation Schedule:
- Database passwords: Every 90 days
- API keys: Every 90 days
- Service account keys: Every 90 days
```

### 4. Enable MFA for All Users

```
Settings > Team > [User] > Require MFA
```

### 5. Review Audit Logs Regularly

```
Settings > Audit Logs
Filter by: User, Action Type, Date Range
Look for: Unusual activity, failed logins, unexpected changes
```

### 6. Use IP Whitelisting (Enterprise)

```yaml
Allowed IPs:
  - 203.0.113.0/24  # Office network
  - 198.51.100.5/32 # VPN endpoint

Block all other IPs: true
```

### 7. Encrypt Sensitive Monitor Queries

```sql
-- Instead of:
SELECT COUNT(*) FROM users WHERE email = 'customer@example.com';

-- Use parameters:
SELECT COUNT(*) FROM users WHERE email = ?;
-- Pass email via encrypted parameter
```

---

## Compliance Assistance (Enterprise)

### Available Services

1. **Compliance Documentation**:
   - SOC 2 reports
   - Data Processing Agreements
   - Security questionnaires
   - Architecture diagrams

2. **Security Reviews**:
   - Annual security review meetings
   - Custom security assessments
   - Vendor security questionnaire assistance

3. **Custom Agreements**:
   - Business Associate Agreement (HIPAA)
   - Data Processing Agreement (GDPR)
   - Custom NDAs
   - Extended retention periods

### Request Compliance Documents

Email: compliance@datapulse.io

Include:
- Company name
- Document needed
- Use case/requirement
- Timeline

---

## Questions?

- **General Security**: security@datapulse.io
- **Compliance**: compliance@datapulse.io
- **HIPAA/BAA**: hipaa@datapulse.io
- **Report Vulnerability**: security@datapulse.io (use PGP)
- **Legal**: legal@datapulse.io

---

## Security Resources

- Security Portal: security.datapulse.io
- Trust Center: trust.datapulse.io
- Status Page: status.datapulse.io
- Privacy Policy: datapulse.io/privacy
- Terms of Service: datapulse.io/terms
