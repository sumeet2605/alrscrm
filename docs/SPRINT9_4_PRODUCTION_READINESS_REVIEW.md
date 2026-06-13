# Sprint 9.4 Production Readiness Review

Scope:

- Production hardening only
- No Finance, Booking, Gallery, Editing, Delivery, or Organization onboarding
  workflow changes

## Current State

ALRSCRM has strong domain coverage through Sprint 9.2, but production
operations are still incomplete. The current application exposes a basic
`/health` endpoint and relies on Docker Compose for local and production-like
deployment. No Terraform files are present in the repository.

## Existing Capabilities

- PostgreSQL is the production database target.
- Alembic migrations exist for all implemented domains.
- Redis is configured and used for login rate limiting.
- DigitalOcean Spaces-compatible object storage is supported.
- Tenant-aware login and token-scoped public Gallery and Delivery access exist.
- Audit logs include organization and branch scope.

## Gaps

| Area | Gap | Severity |
| --- | --- | --- |
| Health checks | Only `/health` exists; no liveness/readiness split. | BLOCKER |
| Readiness | No database, storage, or migration compatibility readiness check. | BLOCKER |
| Logging | Access logs are not standardized as structured JSON. | HIGH |
| Request IDs | No request correlation header is generated or propagated. | HIGH |
| Monitoring | No platform metrics endpoint exists. | HIGH |
| Backup | No backup configuration framework or runbook exists. | BLOCKER |
| Restore | No restore runbook exists. | BLOCKER |
| Secrets | Production validation does not require all runtime secrets independently. | HIGH |
| Docker | Production Compose lacks health checks, resource limits, and full edge deployment controls. | HIGH |
| Cloud Run | No deployment plan exists for Cloud Run. | HIGH |
| Terraform | No Terraform exists in the repository. | MEDIUM |

## Implementation Scope For Sprint 9.4

- Add liveness and readiness endpoints.
- Add structured JSON request logging.
- Add request ID generation and response propagation.
- Propagate request IDs into audit metadata.
- Add in-process metrics collection and a Super Admin metrics API.
- Add backup configuration persistence model.
- Add startup production secrets validation.
- Add operational runbooks and deployment checklist.

## Non-Goals

- No actual cloud backup automation.
- No domain workflow changes.
- No queue/worker implementation.
- No Cloud Run Terraform implementation.
- No Finance, Booking, Gallery, Editing, Delivery, or onboarding logic changes.

## Target Verdict

Sprint 9.4 should move the system from:

```text
NO GO
```

to:

```text
GO WITH FIXES for pilot launch
```

Remaining fixes after Sprint 9.4 should be operational automation, provider
monitoring, and full disaster recovery drills.
