# Sprint 9.3 Production Readiness Audit

Review scope:

- Sprint 1 through Sprint 9.2 repository state
- Multi-tenant SaaS photography CRM production readiness
- Backend, frontend, migrations, Docker configuration, storage, security,
  finance, integrations, and documentation

No backend, frontend, or migration code was modified for this audit.

## Verdict

```text
NO GO for public production SaaS launch.
GO WITH FIXES for staging or a controlled private pilot.
```

The product has a strong domain foundation and the core tenant-scoped workflows
are implemented, but production launch should wait until operational blockers
are closed: backup and restore, monitoring, data retention, production
deployment hardening, and provider-level verification for tenant integrations.

## Severity Scale

| Severity | Meaning |
| --- | --- |
| BLOCKER | Must be fixed before public production launch. |
| HIGH | Should be fixed before launch or formally accepted with mitigation. |
| MEDIUM | Important production hardening or scale follow-up. |
| LOW | Cleanup, polish, or non-critical improvement. |

## Executive Summary

ALRSCRM is now structurally multi-tenant with a shared database and shared
schema. Tenant data is generally scoped by `organization_id`; branch operations
are generally scoped by `branch_id`. Sprint 8.1 hardened login, Gallery public
access, Delivery public access, audit scoping, and bootstrap behavior. Sprint
9.1 introduced Finance as a separate bounded context. Sprint 9.2 introduced
tenant-owned integrations.

The implementation is not yet production-ready for an open SaaS launch because
operational readiness is behind feature readiness. The repository lacks a
complete backup and restore plan, production observability, explicit data
retention policy, provider verification for integrations, and a hardened
deployment topology.

## Findings By Audit Area

| Area | Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- | --- |
| Multi-tenant isolation | HIGH | Tenant isolation is broadly implemented, but platform administration still uses the pseudo-tenant `ALRSCRM`. | `docs/PLATFORM_VS_TENANT_ARCHITECTURE_REVIEW.md`, `backend/scripts/seed_super_admin.py`, `backend/app/identity/models/user.py` | Plan platform identity separation before broad SaaS scale. |
| RBAC consistency | MEDIUM | Route-level permissions are generally present, but platform and tenant roles remain mixed through `Super Admin` as a tenant-shaped user. | `backend/app/identity/policies.py`, `backend/app/identity/seeds.py` | Split platform permissions from tenant permissions in a future architecture migration. |
| Organization onboarding | MEDIUM | Super Admin driven onboarding exists, but no self-service SaaS signup or owner invitation hardening beyond current onboarding scope. | `backend/app/identity/services/organization_service.py`, `frontend/src/modules/organizations` | Keep onboarding platform-admin only until invite, billing, and tenant-aware login UX are finalized. |
| Authentication and JWT | HIGH | Tenant-aware login is implemented, but login rate limiting falls back to process-local memory if Redis is unavailable. | `backend/app/auth/service.py`, `backend/app/auth/rate_limit.py` | In production, rate limiting should fail closed or use highly available Redis. |
| Public Gallery security | MEDIUM | Gallery public access is tokenized and password-aware, but production needs rate limiting, monitoring, and operational link rotation procedures. | `backend/app/galleries/routes.py`, `backend/app/galleries/services/gallery_service.py` | Add public route throttling and operational playbooks. |
| Delivery security | MEDIUM | Delivery token, password, session, signed URL, and reopen controls exist, but artifact generation and delivery operations need background jobs and observability. | `backend/app/delivery/services/delivery_service.py`, `docs/DELIVERY_SECURITY_MODEL.md` | Move expensive delivery operations to an explicit job worker. |
| Finance security | HIGH | Finance is tenant-scoped and separate, but GST invoice PDFs are not yet compliance-validated production templates. | `backend/app/finance/pdf.py`, `docs/SPRINT9_GST_ARCHITECTURE.md` | Validate GST invoice and receipt formats with finance/legal requirements. |
| Tenant integrations security | HIGH | Credentials are encrypted and masked, but verification only validates credential shape instead of provider connectivity. | `backend/app/integrations/services/integration_service.py` | Implement provider-specific verification before treating integrations as production-connected. |
| API authorization gaps | MEDIUM | Most APIs use permission dependencies, but public endpoints and platform workflows require focused abuse testing and monitoring. | `backend/app/api/router.py`, domain route modules | Add API security regression tests for public flows and platform routes. |
| Database constraints and indexes | HIGH | Some nullable unique constraints are service-enforced but not race-safe in PostgreSQL, including organization-level FinanceSettings and integrations. | `backend/alembic/versions/202606100017_create_finance_mvp.py`, `backend/alembic/versions/202606100018_create_tenant_integrations.py` | Add partial unique indexes or normalized branch scope columns. |
| Migration safety | HIGH | Alembic migrations exist and have been verified, but production startup runs migrations without an explicit backup or rollback gate. | `docker-compose.prod.yml`, `backend/alembic/versions` | Add migration runbook, backup preflight, and rollback testing. |
| Audit log coverage | MEDIUM | Audit logs are tenant-scoped after hardening, but event coverage is inconsistent and no audit review/export workflow exists. | `backend/app/shared/services/audit_service.py`, service calls | Define audit event matrix and add tenant-safe audit query tooling. |
| Data retention | BLOCKER | No complete retention policy exists for photos, delivery artifacts, public tokens, refresh sessions, audit logs, or financial documents. | Storage and domain docs | Define retention, deletion, archival, and legal hold policies. |
| Backup and restore | BLOCKER | No production backup service, restore drill, RPO, or RTO is defined in repository deployment assets. | `docker-compose.prod.yml`, docs | Add database and object storage backup/restore runbooks and tests. |
| Storage architecture | HIGH | DigitalOcean Spaces support exists, but CDN URLs can bypass signed URL behavior if configured as public CDN links. | `backend/app/galleries/storage/provider.py` | Ensure private bucket/CDN access model is documented and enforced. |
| Cost optimization | MEDIUM | No lifecycle policies, thumbnail strategy, background processing budget, or storage cost controls are documented. | Storage provider and deployment docs | Add cost controls for media, delivery artifacts, logs, and backups. |
| Monitoring and observability | BLOCKER | No production metrics, tracing, centralized logs, alerting, uptime checks, or audit dashboards are configured. | `backend/app/main.py`, Docker docs | Add observability stack before launch. |
| Error handling | MEDIUM | Application errors are handled, but there is no clear request ID, correlation ID, or global unexpected-exception redaction strategy. | `backend/app/main.py`, `frontend/src/components/ErrorBoundary.tsx` | Add request IDs, structured logs, and global exception handling. |
| Background jobs | HIGH | Long-running or scheduled work is still mostly synchronous or request-driven. | Delivery, sales aging, storage workflows | Add queue/worker architecture for ZIP generation, expiry, notifications, and scheduled aging. |
| Deployment readiness | BLOCKER | Production compose lacks complete TLS/reverse proxy, secret management, health checks, resource limits, backup services, and deployment runbooks. | `docker-compose.prod.yml` | Harden deployment topology before public launch. |

## What Is Production-Strong

- Tenant-aware login uses organization code before user lookup.
- Duplicate emails across organizations are supported by tenant-scoped lookup.
- JWTs carry tenant and branch claims.
- Refresh tokens are hashed, persisted, rotated, and revoked on reuse.
- Public Gallery and Delivery links no longer rely on UUID as the public secret.
- Delivery has token revocation, password support, session tokens, and signed
  download URLs.
- Finance is modeled as a separate bounded context and does not move financial
  lifecycle state into Bookings, Galleries, Editing, or Delivery.
- Tenant integrations store encrypted credentials and return credential keys
  instead of secret values.
- Most domain APIs enforce route-level permissions and service-level tenant
  scope.

## Launch Blockers

| Severity | Blocker | Why It Blocks Launch |
| --- | --- | --- |
| BLOCKER | Backup and restore readiness | A SaaS launch cannot proceed without tested database and media restore. |
| BLOCKER | Monitoring and alerting | Operators cannot detect downtime, auth abuse, storage failures, or payment/reporting failures. |
| BLOCKER | Data retention strategy | Photos, financial records, public links, and audit logs have different legal and operational retention needs. |
| BLOCKER | Deployment hardening | Current production compose is not a complete internet-facing deployment architecture. |

## High Priority Fixes

- Harden Redis/rate-limit behavior for production.
- Add partial unique indexes for nullable organization-level uniqueness.
- Validate GST invoice and receipt PDFs against real statutory requirements.
- Implement provider-specific integration verification.
- Define storage privacy rules for DigitalOcean Spaces and CDN usage.
- Move delivery artifact generation and scheduled domain transitions to a
  worker architecture.
- Add migration backup and rollback gates.

## Recommended Release Path

1. Close all `BLOCKER` items.
2. Close or explicitly accept all `HIGH` security and data-integrity items.
3. Run a restore drill using a production-like database and object storage
   bucket.
4. Run a tenant isolation security test suite with at least two organizations
   and duplicate user emails.
5. Run load and abuse tests against login, public Gallery, public Delivery,
   Finance PDFs, and integrations.
6. Launch as a controlled private pilot before open SaaS availability.

## Final Recommendation

```text
NO GO for public production launch.
GO WITH FIXES for staging and controlled private pilot.
```

The repository is functionally advanced enough for pilot validation, but the
operational layer must be strengthened before ALRSCRM is treated as a public
multi-tenant SaaS production system.
