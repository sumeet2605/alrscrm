# SaaS Production Readiness Review

Review date: 2026-06-11

Reviewed branch: `development`

Scope reviewed:

- Sprint 1 Identity and Access
- Sprint 2 Family
- Sprint 3 Sales Opportunity
- Sprint 4 Booking Fulfillment
- Sprint 5 Gallery
- Sprint 6 Editing
- Sprint 7 Delivery
- Sprint 7.1 Delivery Hardening
- Sprint 8 SaaS Organization Onboarding
- Backend APIs, models, services, repositories, migrations, tests, frontend
  routes, frontend modules, Docker, and CI

No implementation changes were made as part of this review.

## Executive Summary

ALRSCRM has a real multi-organization foundation: most business tables carry
`organization_id`, most operational flows carry `branch_id`, and services
usually enforce scope through `AuthorizationContext`. The repository is a
shared database, shared schema SaaS architecture.

The system is not yet ready for broad commercial SaaS production with multiple
external studios and real customer photo data. The main blockers are
tenant-aware login, public Gallery sharing security, bootstrap secret handling,
organization owner onboarding, and operational hardening.

Recommended decision:

```text
NO-GO for open commercial SaaS production.
GO for controlled internal or pilot use after environment secrets are hardened.
```

## Readiness Scores

| Area | Score |
| --- | ---: |
| Overall Completion | 72% |
| Production Readiness | 58% |
| SaaS Readiness | 55% |
| Security Score | 6.5 / 10 |
| DDD Score | 7 / 10 |
| Test Coverage Score | 6.5 / 10 |

These scores reflect implemented feature breadth plus release risk. Feature
coverage is high, but SaaS readiness is held back by tenant login, public
sharing, onboarding security, and production operations.

## 1. Multi Tenant Review

### Architecture Type

ALRSCRM uses:

```text
Shared Database, Shared Schema
```

Evidence:

- Migrations create shared tables such as `organizations`, `branches`,
  `families`, `opportunities`, `bookings`, `galleries`, `editing_jobs`, and
  `delivery_jobs`.
- Tenant isolation is represented by `organization_id`.
- Branch isolation is represented by `branch_id`.
- There is no tenant-specific schema or database provisioning logic.

### Tenant Boundary

`organization_id` is the tenant boundary.

Evidence:

- `backend/app/identity/services/organization_service.py` scopes non-platform
  organization listing to `Organization.id == context.organization_id`.
- Family, booking, gallery, editing, and delivery repositories accept or store
  `organization_id`.
- Delivery audit records include `organization_id` and `branch_id`.

### Branch Boundary

`branch_id` is the operational branch boundary.

Evidence:

- `AuthorizationContext.is_branch_scoped` is used across services.
- Family listing filters by `Family.branch_id`.
- Booking listing filters by `Booking.branch_id`.
- Gallery storage paths include organization, branch, gallery, and file name.
- Delivery scope checks reject cross-branch access for branch-scoped users.

### Modules Enforcing Tenant Isolation

| Module | Status | Evidence |
| --- | --- | --- |
| Identity | Mostly enforced | Organization, branch, and user services use `AuthorizationContext`. |
| Family | Mostly enforced | Repository filters by `organization_id` and `branch_id`; service validates branch scope. |
| Sales | Mostly enforced | Opportunity and follow-up flows are organization and branch scoped after Sprint 3 hardening. |
| Bookings | Mostly enforced | Booking, package, addon, schedule, and assignment queries apply scope through service and repository. |
| Galleries | Partially enforced | Staff APIs are scoped; public gallery links bypass tenant auth by design. |
| Editing | Mostly enforced | Editing jobs carry organization and branch, and workflow services check scope. |
| Delivery | Strongest public model | Delivery uses opaque access tokens, hashed tokens, expiry, revocation, sessions, and audit records. |
| Organization Settings | Enforced | Settings are accessed through organization service scope checks. |

### Modules Needing Hardening

#### Critical: Login Is Not Tenant-Aware

`backend/app/auth/service.py` authenticates by email only:

```text
authenticate_user() -> get_user_by_email(db, email)
```

`backend/app/identity/services/user_service.py` implements
`get_user_by_email()` with only:

```text
User.email == normalized_email
```

This conflicts with SaaS onboarding, where `User` uniqueness is modeled per
organization. Duplicate owner emails across organizations cannot be reliably
authenticated without tenant context.

Severity: Critical

Affected files:

- `backend/app/auth/service.py`
- `backend/app/identity/services/user_service.py`
- `frontend/src/pages/LoginPage.tsx`
- `docs/TENANT_AWARE_LOGIN_DESIGN.md`

Recommended fix:

- Add tenant-aware login using organization code, subdomain, custom domain, or
  a deliberate global-identity design.
- Prefer `organization_code + email + password` for the next hardening sprint.
- Add tests for duplicate email across two organizations.

#### Critical: Public Gallery Sharing Is Weaker Than Delivery Sharing

Gallery public access uses the Gallery UUID:

- `GET /api/v1/galleries/{gallery_id}/public`
- `POST /api/v1/galleries/{gallery_id}/public/favorites`
- `POST /api/v1/galleries/{gallery_id}/public/submit-selection`

Password protection is optional. If a gallery has no password and has not
expired, the UUID functions as the public secret.

Severity: Critical for private customer photos

Affected files:

- `backend/app/galleries/routes.py`
- `backend/app/galleries/services/gallery_service.py`
- `frontend/src/api/galleries.ts`
- Gallery public frontend pages

Recommended fix:

- Move Gallery public access to the hardened Delivery model:
  opaque token, token hash storage, revocation, expiry, session token, audit,
  and rate limiting.
- Keep UUIDs internal only.

#### Major: Gallery Password Authentication Expiry Check Is Unreachable

In `backend/app/galleries/services/gallery_service.py`,
`authenticate_public_gallery()` contains an expiry check nested after:

```text
if gallery is None:
    raise NotFoundError("Gallery not found")
    if gallery.expires_at is not None:
        ...
```

The expiry block is unreachable. An expired password-protected gallery can still
issue a gallery access token before later public reads reject the expired
gallery.

Severity: Major

Recommended fix:

- Move expiry validation outside the `gallery is None` block.
- Add tests for authenticating an expired password-protected gallery.

#### Major: General Audit Logs Are Not First-Class Tenant Scoped

`backend/app/shared/models/audit_log.py` stores:

- `actor_user_id`
- `action`
- `target_type`
- `target_id`
- `metadata_json`
- `created_at`

It does not store first-class `organization_id` or `branch_id`. Some services
write organization and branch into metadata, and Delivery has its own scoped
audit table, but the shared audit table cannot be safely queried by tenant
without joins or metadata inspection.

Severity: Major

Recommended fix:

- Add nullable `organization_id` and `branch_id` columns to `audit_logs`.
- Backfill where practical.
- Require future audit writes to provide scope.

### Routes Or Queries With Cross-Tenant Risk

| Area | Risk |
| --- | --- |
| Auth login | Email-only lookup is not tenant-aware. |
| Public Gallery | UUID-based access can expose customer photos if a link leaks. |
| Public Gallery auth | Expiry check bug allows token issuance for expired galleries. |
| General AuditLog | Tenant-safe audit review/export is weak. |
| Bootstrap seeding | Hardcoded credentials can affect production tenant security. |

## 2. DDD Review

### Aggregate Boundaries

| Aggregate | Current Boundary | Assessment |
| --- | --- | --- |
| Organization | Tenant aggregate | Correct for SaaS tenant ownership. |
| Branch | Organization-owned operational boundary | Correct. |
| User | Identity aggregate/entity under Organization | Mostly correct. |
| Family | Customer profile aggregate | Correct. Customer profile data is not duplicated into Opportunity, Booking, Editing, or Delivery persistence. |
| Opportunity | Sales aggregate root | Correct. References `family_id`. |
| FollowUp | Opportunity-owned child | Correct. |
| LostReason | Sales reference entity | Correct and database-driven. |
| Booking | Booking aggregate root | Correct. References Family and Opportunity. |
| Package | Booking reference/config entity | Correct as branch-scoped catalog data. |
| Gallery | Selection aggregate | Correct, but public access model needs security hardening. |
| EditingJob | Production aggregate root | Correct. |
| DeliveryJob | Delivery aggregate root | Correct. Delivery hardening is stronger than Gallery. |

### DDD Violations And Weaknesses

#### Service-Centric Domain Behavior

Most domain invariants live in service functions rather than aggregate methods.
This is pragmatic for the current FastAPI and SQLAlchemy codebase, but it
weakens explicit domain modeling.

Severity: Medium

Examples:

- Opportunity stage transitions.
- Gallery selection submission.
- Editing workflow transitions.
- Delivery lifecycle transitions.

Recommended fix:

- Keep services as transaction/application boundaries.
- Gradually move high-value invariants into aggregate methods where it reduces
  risk and improves testability.

#### Audit Events Are Not True Domain Events

The system records audit-backed events, but there is no outbox, event bus, or
durable integration event mechanism.

Severity: Medium

Recommended fix:

- Add an outbox before driving async workflows, notifications, or integrations
  from event records.

#### Family Child Updates Still Obscure Intent

Family nested updates still replace collections for members and service
interests. This is acceptable for CRUD but weak for future timeline, audit, and
event semantics.

Severity: Low to Medium

Recommended fix:

- Add explicit child operations only when timeline or workflow requirements
  need them.

## 3. Security Review

### Positive Findings

- Passwords are hashed.
- Refresh tokens rotate and are hashed server-side.
- RBAC is enforced on backend routes.
- Delivery public links use opaque tokens, token hashes, expiry, revocation,
  and session tokens.
- Delivery public download uses signed artifact URLs.
- Most services reject cross-organization and cross-branch access.
- CI runs backend lint, migrations, tests, frontend lint, tests, build, and
  Docker image build.

### Critical Findings

#### Hardcoded Bootstrap Credentials

`backend/scripts/seed_super_admin.py` contains:

- `ADMIN_PASSWORD = "Admin@123"`
- `SAMPLE_OWNER_PASSWORD = "Owner@123"`

`docker-compose.prod.yml` runs:

```text
python -m scripts.seed_super_admin
```

The script also resets an existing user's password when it finds the user.

Severity: Critical

Impact:

- Production startup can restore a known admin password.
- Sample owner credentials are static when sample tenant seeding is enabled.
- Password rotation can be undone by deployment.

Recommended fix:

- Require environment-provided one-time bootstrap secrets in non-local
  environments.
- Never reset an existing admin password unless an explicit recovery flag is
  set.
- Force password reset on first login for bootstrap-created users.

#### Tenant-Aware Login Missing

See Multi Tenant Review. This is both a SaaS and security issue.

Severity: Critical

#### Public Gallery Token Model Needs Hardening

See Multi Tenant Review.

Severity: Critical

### Major Findings

#### Onboarding Returns Temporary Password In API Response

`organization_service.onboard_organization()` generates a temporary password
and returns it with the onboarding response.

Severity: Major

Impact:

- Temporary passwords can be exposed in browser devtools, logs, monitoring, or
  support screenshots.
- There is no owner invite or one-time password setup flow.

Recommended fix:

- Replace returned password with an invite token and secure password setup
  workflow.
- Store invite token hash and expiry.

#### Login Rate Limit Falls Back To Process Memory

`backend/app/auth/rate_limit.py` uses Redis when available and falls back to
`_local_attempts` on Redis errors.

Severity: Medium to Major

Impact:

- Multiple API replicas would not share local fallback state.
- Redis outages weaken brute-force protection.

Recommended fix:

- Require Redis for production auth rate limiting.
- Include tenant identifier in the rate-limit key once tenant-aware login is
  implemented.

## 4. SaaS Readiness Review

### Implemented

- Organization CRUD APIs.
- Organization onboarding endpoint.
- Organization settings entity and APIs.
- Frontend organization list, onboarding, and detail pages.
- Platform Super Admin organization management permissions.
- Shared-schema multi-tenant model.
- Branch management.
- User and role management.

### Missing Or Incomplete

| Capability | Status |
| --- | --- |
| Tenant-aware login | Missing |
| Owner invite flow | Missing |
| Public self-signup | Intentionally not implemented |
| Subscription and billing | Missing |
| Plan limits | Missing |
| Tenant status enforcement beyond `is_active` | Partial |
| Custom domain/subdomain routing | Missing |
| Organization branding applied to public pages | Partial or missing |
| Tenant-specific storage policy UI | Missing |
| Tenant offboarding/export | Missing |
| Tenant audit export | Weak due to audit schema |

### SaaS Product Risk

Sprint 8 establishes organization onboarding, but the app still behaves more
like a platform-admin-managed multi-tenant system than a self-serve SaaS
product.

Recommended next SaaS work:

- Tenant-aware login.
- Owner invite and password setup.
- Organization lifecycle states.
- Billing/subscription module.
- Plan limit enforcement.
- Tenant support tooling.

## 5. Scalability Review

### Positive Findings

- PostgreSQL is the primary persistence layer.
- Redis is present for auth rate limiting.
- Pagination exists for major list APIs.
- Delivery access tokens are hashed and indexed through repository lookup.
- Delivery number generation uses a sequence.
- Gallery file paths include organization and branch identifiers.
- Family code generation uses PostgreSQL sequence when available.

### Scalability Risks

#### Synchronous Public And Workflow Operations

ZIP generation and large media workflows should be asynchronous at scale.
Delivery ZIP generation currently creates an artifact through the storage
abstraction but does not package real image binaries.

Severity: Major

Recommended fix:

- Add background job infrastructure.
- Add storage source reads and actual ZIP packaging.
- Track job progress and retry state.

#### Metrics And Dashboards Need Reporting Strategy

Dashboards currently calculate metrics from operational tables. This is fine at
current scale but can become expensive.

Severity: Medium

Recommended fix:

- Add composite indexes for common tenant, branch, status, and date filters.
- Introduce read models or reporting tables once query volume grows.

#### Local Fallback Rate Limiting Does Not Scale

See Security Review.

Severity: Medium

#### Storage Isolation Is Path-Based

Storage paths include organization and branch, which is good. Strong production
hardening still needs object-store bucket policies, lifecycle rules, CDN rules,
and signed URL expiry policies.

Severity: Medium

## 6. DevOps Review

### Positive Findings

- GitHub Actions CI exists at `.github/workflows/ci.yml`.
- CI runs backend Ruff, Alembic migrations, backend tests, Docker image build,
  frontend lint, frontend tests, and frontend build.
- Docker Compose includes API, PostgreSQL, and Redis.
- PostgreSQL uses a named Docker volume in production compose.

### Gaps

| Area | Gap |
| --- | --- |
| Secrets | Bootstrap passwords are hardcoded in script. |
| API healthcheck | Docker compose does not define an API healthcheck. |
| Backups | No backup or restore runbook found. |
| Observability | No metrics, tracing, alerting, or structured log strategy found. |
| Deployment | Compose exists, but no production deployment pipeline/runbook was found. |
| Object storage | DigitalOcean Spaces support exists through storage abstraction, but operational docs need hardening. |
| Migration safety | CI runs migrations, but rollback strategy and production migration runbook are missing. |

### Recommended Fixes

- Remove known-password bootstrap behavior before production.
- Add API healthcheck.
- Add backup and restore documentation.
- Add structured logs, metrics, and error reporting.
- Add production migration runbook.
- Add environment validation at startup for required production secrets.

## 7. QA Review

### Current Test Position

Sprint 8 report states:

```text
backend tests: 55 passed
frontend tests: 32 passed
```

CI also runs:

- Backend lint.
- Alembic migration upgrade.
- Backend tests.
- Frontend lint.
- Frontend tests.
- Frontend build.
- Docker image build.

### Strengths

- Backend API tests exist for identity, auth, families, sales, bookings,
  galleries, editing, delivery, and bootstrap.
- Frontend tests exist for login, protected routes, dashboard layout,
  organization pages, delivery pages, editing queue, and other core modules.
- Migration upgrade is validated in CI.

### Missing Test Coverage

| Gap | Severity |
| --- | --- |
| Duplicate email across two organizations login behavior | Critical |
| Public Gallery expired password authentication | Critical |
| Public Gallery token hardening and revocation | Major |
| Organization owner invite/password setup | Major |
| Cross-tenant tests for every dashboard and metrics endpoint | Major |
| Storage isolation tests against Spaces-compatible provider | Major |
| Backup and restore verification | Major |
| Browser E2E tests for onboarding, gallery selection, editing, and delivery | Major |
| Load tests for dashboards, gallery photo grids, and delivery downloads | Medium |
| RBAC negative tests for all role/module combinations | Medium |

### QA Recommendation

Before production SaaS launch, add a dedicated hardening test suite for:

- Multi-tenant isolation.
- Branch isolation.
- Public access security.
- Organization onboarding.
- Bootstrap idempotency and secret handling.
- Object storage behavior.

## 8. Product Review

### Product Capability Implemented

ALRSCRM now covers a broad studio operating flow:

- Identity and RBAC.
- Branches and users.
- Families.
- Opportunities and follow-ups.
- Bookings, packages, schedules, and assignments.
- Galleries and client selection.
- Editing production.
- Delivery management.
- Organization onboarding.

### Product Gaps For SaaS Launch

| Gap | Impact |
| --- | --- |
| Tenant-aware login | Blocks reliable multi-tenant SaaS identity. |
| Owner invite flow | Onboarding is operationally unsafe. |
| Public Gallery sharing model | Private photo risk. |
| Billing/subscription | Cannot monetize as SaaS. |
| Plans and quotas | No limit enforcement per tenant. |
| Email/WhatsApp notifications | Operational workflows require manual communication. |
| Tenant branding | Public client pages may not fully reflect each studio. |
| Support tooling | Platform support cannot safely inspect/export tenant context. |
| Reporting exports | Studio reporting is incomplete for business operations. |

### Product Recommendation

The product is close to a strong managed internal platform. It needs another
hardening sprint before paid SaaS onboarding.

## 9. Technical Debt Review

### High-Value Debt

1. Tenant-aware identity is designed but not implemented.
2. Public Gallery access uses UUIDs instead of opaque, revocable links.
3. Bootstrap script resets known credentials.
4. General audit logs are not tenant scoped.
5. Organization onboarding returns temporary passwords.
6. Delivery artifact generation does not package actual photo binaries yet.
7. Domain behavior is mostly service-centric.
8. Audit-backed events are not outbox-backed events.
9. API response envelopes weaken generated OpenAPI type precision.
10. Frontend route visibility is role-name based while backend RBAC is
    permission based.

### Medium Debt

- Dashboard/reporting queries need a long-term read model strategy.
- Public Gallery favorite count updates are not fully transactional.
- Object storage needs production lifecycle, CDN, and backup policies.
- E2E and load testing are missing.
- API health, metrics, logging, and alerting need production hardening.

## 10. Final Executive Report

### Top 20 Risks

| Rank | Risk | Severity |
| ---: | --- | --- |
| 1 | Login is not tenant-aware and cannot safely support duplicate tenant emails. | Critical |
| 2 | Public Gallery sharing uses UUID-based links and optional passwords. | Critical |
| 3 | Bootstrap script contains and resets known passwords. | Critical |
| 4 | Expired password-protected galleries can still issue auth tokens due to unreachable expiry check. | Major |
| 5 | Organization onboarding returns temporary owner passwords in API responses. | Major |
| 6 | General audit logs lack first-class tenant and branch columns. | Major |
| 7 | Delivery ZIP artifact does not package real final image binaries yet. | Major |
| 8 | No production backup/restore runbook is present. | Major |
| 9 | No observability, metrics, tracing, or alerting strategy is present. | Major |
| 10 | Auth rate-limit fallback is per-process memory. | Major |
| 11 | Billing, subscriptions, plan limits, and quota enforcement are missing. | Major |
| 12 | Public Gallery selection count updates use separate commits and swallowed exceptions. | Medium |
| 13 | Dashboard/reporting queries may become expensive at scale. | Medium |
| 14 | No full browser E2E suite for critical workflows. | Medium |
| 15 | No load testing for gallery, delivery, and dashboard workloads. | Medium |
| 16 | No formal tenant offboarding/export flow. | Medium |
| 17 | API response envelopes reduce generated TypeScript precision. | Medium |
| 18 | Domain events are audit-backed only; no outbox exists. | Medium |
| 19 | Frontend route permissions use role names for display gating. | Low to Medium |
| 20 | Production deployment runbook is incomplete. | Medium |

### Recommended Sprint Sequence After Sprint 8.1

#### Sprint 8.1: SaaS Security Hardening

- Implement tenant-aware login.
- Remove known-password bootstrap behavior.
- Replace public Gallery UUID access with opaque token access.
- Fix Gallery password-auth expiry validation.
- Add tenant and branch columns to shared audit logs.
- Add cross-tenant security regression tests.

#### Sprint 8.2: Organization Owner Lifecycle

- Replace temporary password response with invite flow.
- Add owner password setup.
- Add invite expiry, revocation, and audit.
- Add organization lifecycle states.
- Add tenant support tooling basics.

#### Sprint 9: Billing And Plans

- Add subscription/account plan model.
- Add plan limits for users, branches, storage, galleries, and downloads.
- Add payment integration and invoice lifecycle.
- Add tenant suspension behavior.

#### Sprint 10: Production Operations

- Add API healthchecks.
- Add backup and restore runbooks.
- Add structured logging, metrics, tracing, and alerting.
- Add production migration runbook.
- Add environment validation for production.

#### Sprint 11: Media And Storage Hardening

- Package actual edited images into delivery ZIP files.
- Add async media jobs.
- Add DigitalOcean Spaces lifecycle and CDN documentation.
- Add storage integration tests.

#### Sprint 12: QA And Compliance

- Add E2E tests.
- Add load tests.
- Add audit export.
- Add tenant data export/offboarding.
- Add security regression suite.

### GO / NO-GO

```text
NO-GO for broad commercial SaaS production.
GO for controlled pilot use with trusted internal users after bootstrap secrets
are fixed and public Gallery sharing is restricted or hardened.
GO for continuing SaaS investment; the architecture is directionally correct.
```

### Final Recommendation

ALRSCRM has the right shared-schema multi-tenant foundation and a broad domain
surface. The next work should not add more business features. The next sprint
should be a hardening sprint focused on tenant-aware login, public Gallery
security, bootstrap secrets, tenant-scoped audit logs, and invite-based
organization onboarding.
