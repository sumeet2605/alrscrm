# Sprint 9.3 Launch Checklist

This checklist converts the production audit into launch gates.

No backend, frontend, or migration code was modified for this checklist.

## Launch Verdict

```text
NO GO for public production launch today.
GO WITH FIXES for staging or controlled private pilot.
```

## Blocker Gate

All `BLOCKER` items must be complete before public launch.

| Status | Severity | Item | Owner |
| --- | --- | --- | --- |
| Not Ready | BLOCKER | PostgreSQL automated backups configured. | DevOps |
| Not Ready | BLOCKER | Object storage backup or replication configured. | DevOps |
| Not Ready | BLOCKER | Restore drill completed and documented. | DevOps |
| Not Ready | BLOCKER | RPO and RTO targets approved. | Product/Engineering |
| Not Ready | BLOCKER | Centralized logs configured. | DevOps |
| Not Ready | BLOCKER | Metrics and alerting configured. | DevOps |
| Not Ready | BLOCKER | Error tracking configured. | Engineering |
| Not Ready | BLOCKER | Production reverse proxy and TLS configured. | DevOps |
| Not Ready | BLOCKER | Data retention policy approved. | Product/Legal/Engineering |
| Not Ready | BLOCKER | Public Gallery and Delivery operational monitoring enabled. | Engineering |

## High Priority Security Gate

These items should be complete before launch unless explicitly accepted with a
documented mitigation.

| Status | Severity | Item | Owner |
| --- | --- | --- | --- |
| Not Ready | HIGH | Redis rate limiting is production-required and monitored. | Backend/DevOps |
| Not Ready | HIGH | Dedicated integration encryption key required in production. | Backend/DevOps |
| Not Ready | HIGH | Tenant integration verification calls provider APIs. | Backend |
| Not Ready | HIGH | DigitalOcean Spaces bucket/CDN privacy model verified. | Backend/DevOps |
| Not Ready | HIGH | Finance GST invoice PDF validated for real use. | Product/Finance/Backend |
| Not Ready | HIGH | Nullable unique constraints protected with database-level partial indexes. | Backend |
| Not Ready | HIGH | Migration runbook includes backup and rollback gates. | Release Manager |
| Not Ready | HIGH | Background worker architecture planned for artifact generation and scheduled jobs. | Backend |
| Not Ready | HIGH | Platform identity separation roadmap approved. | Architecture |

## Multi-Tenant Gate

| Status | Severity | Item |
| --- | --- | --- |
| Ready | MEDIUM | Tenant-aware login requires organization code. |
| Ready | MEDIUM | Duplicate emails across organizations are supported. |
| Ready | MEDIUM | JWTs include tenant and branch claims. |
| Ready | MEDIUM | Public Gallery links are tokenized. |
| Ready | MEDIUM | Public Delivery links are tokenized. |
| Not Ready | HIGH | Platform Super Admin is separated from tenant organizations. |
| Not Ready | HIGH | Finance/integration nullable uniqueness is enforced at DB level. |
| Not Ready | MEDIUM | Tenant isolation regression suite covers every module and metric. |
| Not Ready | MEDIUM | Branch override policy for integrations is documented. |

## RBAC And API Gate

| Status | Severity | Item |
| --- | --- | --- |
| Ready | MEDIUM | Backend route permissions are broadly implemented. |
| Ready | MEDIUM | Frontend navigation uses permission-aware route config. |
| Not Ready | MEDIUM | Automated audit confirms every authenticated API route has permission dependency. |
| Not Ready | MEDIUM | Public API abuse tests are complete. |
| Not Ready | MEDIUM | Platform-only and tenant-only permissions are separated. |

## Finance Gate

| Status | Severity | Item |
| --- | --- | --- |
| Ready | MEDIUM | Invoice is modeled as financial source of truth. |
| Ready | MEDIUM | Booking monetary fields remain compatibility snapshots. |
| Ready | MEDIUM | Payment entity exists. |
| Ready | MEDIUM | Finance metrics API exists. |
| Not Ready | HIGH | GST invoice PDF legally validated. |
| Not Ready | MEDIUM | Tenant/branch invoice sequence policy finalized. |
| Not Ready | MEDIUM | Credit Notes and Debit Notes remain future scope and are excluded from launch claims. |
| Not Ready | MEDIUM | Finance audit/report export workflow defined. |

## Integrations Gate

| Status | Severity | Item |
| --- | --- | --- |
| Ready | MEDIUM | Tenant-owned integration aggregate exists. |
| Ready | MEDIUM | Credentials are encrypted and masked in API responses. |
| Ready | MEDIUM | Integration health dashboard exists. |
| Not Ready | HIGH | Provider verification calls external providers. |
| Not Ready | HIGH | Secret rotation procedure documented. |
| Not Ready | MEDIUM | Expired credential detection runs on a schedule. |
| Not Ready | MEDIUM | Organization-wide vs branch integration precedence documented. |

## Storage Gate

| Status | Severity | Item |
| --- | --- | --- |
| Ready | MEDIUM | DigitalOcean Spaces provider exists. |
| Ready | MEDIUM | Signed URLs are supported. |
| Not Ready | HIGH | CDN mode cannot bypass protected media access. |
| Not Ready | HIGH | Object storage lifecycle policy configured. |
| Not Ready | MEDIUM | Upload validation and scanning strategy defined. |
| Not Ready | MEDIUM | Tenant storage usage metrics available. |

## Deployment Gate

| Status | Severity | Item |
| --- | --- | --- |
| Not Ready | BLOCKER | Production TLS/reverse proxy configured. |
| Not Ready | BLOCKER | Health checks configured for API, DB, Redis, and storage. |
| Not Ready | HIGH | Container resource limits configured. |
| Not Ready | HIGH | Secrets managed outside plain local files. |
| Not Ready | HIGH | Database migrations are run through release procedure. |
| Not Ready | MEDIUM | Load testing completed. |
| Not Ready | MEDIUM | Incident response runbook created. |

## Monitoring Gate

| Status | Severity | Item |
| --- | --- | --- |
| Not Ready | BLOCKER | Error tracking enabled. |
| Not Ready | BLOCKER | Centralized logs enabled. |
| Not Ready | BLOCKER | Alerts for API downtime enabled. |
| Not Ready | HIGH | Alerts for auth abuse enabled. |
| Not Ready | HIGH | Alerts for storage failures enabled. |
| Not Ready | HIGH | Alerts for migration failure enabled. |
| Not Ready | MEDIUM | Tenant-level operational dashboard created. |

## Data Retention Gate

| Status | Severity | Item |
| --- | --- | --- |
| Not Ready | BLOCKER | Photo retention policy approved. |
| Not Ready | BLOCKER | Delivery artifact retention policy approved. |
| Not Ready | BLOCKER | Financial document retention policy approved. |
| Not Ready | HIGH | Audit log retention policy approved. |
| Not Ready | HIGH | Public token/session cleanup scheduled. |
| Not Ready | MEDIUM | Tenant export/delete policy designed. |

## Recommended Sprint Breakdown

### Sprint 9.4 Production Operations Hardening

- Backup and restore automation.
- Observability stack.
- Production deployment topology.
- Migration runbook.
- Redis production enforcement.
- Storage privacy and lifecycle controls.

### Sprint 9.5 Security And Compliance Hardening

- Platform identity separation design implementation.
- Provider-level integration verification.
- GST PDF compliance validation.
- Tenant isolation regression suite.
- Audit event matrix and audit query/export APIs.
- Data retention implementation.

## Final Launch Checklist Decision

```text
NO GO for public production launch.
```

The checklist should be revisited after all blocker gates are closed and high
severity security items are either fixed or formally accepted by the release
owner.
