# Sprint 9.3 Deployment Review

Review scope:

- Docker deployment assets
- Configuration and secrets
- Database and migrations
- Redis and rate limiting
- Storage architecture
- Backups and restore
- Monitoring and observability
- Background jobs
- Cost controls

No backend, frontend, or migration code was modified for this review.

## Deployment Verdict

```text
NO GO for public production launch.
GO WITH FIXES for staging or controlled private pilot.
```

The deployment layer is the least production-ready part of the system. The
domain implementation is ahead of operational readiness.

## Deployment Findings

| Severity | Finding | Evidence | Recommendation |
| --- | --- | --- | --- |
| BLOCKER | No tested backup and restore strategy is defined for PostgreSQL or object storage. | `docker-compose.prod.yml`, docs | Add automated backups, restore drills, RPO/RTO, and runbooks. |
| BLOCKER | No production monitoring, alerting, tracing, or centralized logs are configured. | `backend/app/main.py`, compose files | Add metrics, structured logs, alerting, uptime checks, and error tracking. |
| BLOCKER | Production compose is not a complete internet-facing deployment topology. | `docker-compose.prod.yml` | Add reverse proxy/TLS, health checks, resource limits, network isolation, and deployment docs. |
| BLOCKER | No complete data retention policy exists. | Domain docs and storage implementation | Define retention for photos, delivery artifacts, invoices, audit logs, tokens, and backups. |
| HIGH | Migrations run without a documented preflight backup and rollback gate. | Docker deployment command pattern | Require backup before migration and rollback-tested release procedures. |
| HIGH | Redis is operationally required for production-grade login throttling, but app falls back to memory. | `backend/app/auth/rate_limit.py` | Make Redis a production dependency with health checks and alerts. |
| HIGH | DigitalOcean Spaces support exists, but CDN/public access mode needs strict deployment guidance. | `backend/app/galleries/storage/provider.py` | Use private buckets and signed URLs unless CDN is access-controlled. |
| HIGH | No background worker architecture is configured for long-running or scheduled work. | Delivery, Sales, storage workflows | Add queue/worker service and scheduled job runner. |
| MEDIUM | Database pool defaults may be too small or too generic for production load. | `backend/app/core/config.py` | Tune pool size, max overflow, statement timeouts, and connection limits. |
| MEDIUM | No resource limits or autoscaling guidance is present. | `docker-compose.prod.yml` | Add CPU/memory limits and scaling strategy. |
| MEDIUM | No cost monitoring or lifecycle policies are documented for media storage and backups. | Storage provider/docs | Add object lifecycle policies and cost dashboards. |
| LOW | Existing build warnings should be cleaned before launch freeze. | Sprint completion reports | Reduce frontend bundle size and clean test warnings. |

## Current Deployment Shape

Current production deployment assets provide:

- API service
- PostgreSQL service
- Redis service
- Alembic migration path
- Environment-file based configuration
- DigitalOcean Spaces capable storage provider

Missing for public production:

- TLS termination
- Reverse proxy
- WAF or edge protection decision
- API health checks beyond basic app health
- Container resource limits
- Centralized log shipping
- Metrics and alerting
- Backup service
- Restore validation
- Background worker service
- Secrets manager
- Deployment rollback procedure

## Configuration And Secrets

Current strengths:

- Non-local environments reject default or weak JWT secret.
- DigitalOcean Spaces settings are validated when Spaces storage is selected.
- Bootstrap password hardening was added in Sprint 8.1.
- Tenant integration credentials are encrypted at rest.

Risks:

- Secrets are environment-file based.
- Dedicated integration encryption key should be mandatory in production.
- Secret rotation is not documented.
- Provider credentials for tenant integrations need lifecycle and revocation
  procedures.

Recommendation:

```text
Move production secrets to a managed secret store or protected deployment
secret mechanism, and document rotation for JWT, integration encryption, object
storage, SMTP, and Meta credentials.
```

## Database And Migration Readiness

Current strengths:

- Alembic migrations exist for all implemented domains.
- Recent sprint validation reported successful `alembic upgrade head`.
- Migrations include constraints and indexes for many tenant-scoped records.

Risks:

- Migration execution is not gated by backup.
- No documented rollback test exists for production data.
- Some nullable unique constraints need partial indexes.
- No database monitoring, slow query monitoring, or query timeout policy is
  documented.

Recommendation:

```text
Add a release migration runbook with backup, dry-run, upgrade, smoke test,
rollback decision point, and restore drill.
```

## Storage Readiness

Current strengths:

- Local provider exists for development.
- DigitalOcean Spaces provider supports private object uploads.
- Signed URL generation exists.

Risks:

- Local provider is metadata/data-url oriented and not production storage.
- CDN URL mode can return non-expiring public URLs if configured that way.
- No storage lifecycle, retention, replication, or disaster recovery policy is
  documented.
- No malware/content scanning is present for uploads.

Recommendation:

```text
Use DigitalOcean Spaces or equivalent object storage for production, private by
default, with signed URLs, lifecycle policies, backups/replication, and access
logs.
```

## Background Job Readiness

The system currently lacks a formal background job architecture.

Work that should move to jobs:

- Delivery ZIP/artifact generation
- Gallery and Delivery expiry enforcement
- Sales follow-up status aging
- Email/WhatsApp/notification sending when implemented
- Storage cleanup
- Token/session cleanup
- Integration health verification
- Report generation

Required design:

- Job table or queue
- Worker process
- Tenant and branch columns on jobs
- Retry policy
- Dead-letter policy
- Idempotency keys
- Operational dashboard

## Monitoring And Observability Readiness

Missing production controls:

- Request IDs
- Structured JSON logs
- Centralized log shipping
- Metrics endpoint
- Error tracking
- Distributed tracing
- Database metrics
- Redis metrics
- Object storage error monitoring
- Authentication abuse alerts
- Public Gallery and Delivery abuse alerts
- Finance PDF/report failure alerts

Recommendation:

```text
Add observability before public launch. Operators need to know when tenant data
access, public link access, storage, and finance workflows fail.
```

## Backup And Restore Readiness

Required before launch:

- PostgreSQL automated backups
- Point-in-time recovery decision
- Object storage backup/replication
- Backup encryption
- Restore drill in staging
- RPO and RTO targets
- Backup alerting
- Documentation for partial tenant recovery

Current status:

```text
Not production-ready.
```

## Cost Optimization Review

Cost risks:

- Original photos, thumbnails, delivery artifacts, and generated ZIPs can grow
  quickly.
- No lifecycle rules are documented.
- No cleanup job exists for expired public sessions or stale artifacts.
- No tenant-level storage metering exists for future platform billing.

Recommendation:

```text
Add storage lifecycle rules, tenant storage metrics, and artifact cleanup before
scale.
```

## Deployment Launch Decision

```text
NO GO for public production launch.
```

Deployment must be hardened before launch even if application workflows pass.
