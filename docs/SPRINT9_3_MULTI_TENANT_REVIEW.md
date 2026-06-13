# Sprint 9.3 Multi-Tenant Review

Review scope:

- Shared database and shared schema tenant model
- `organization_id` tenant boundary
- `branch_id` operational boundary
- Identity, Families, Sales, Bookings, Galleries, Editing, Delivery, Finance,
  and Integrations

No backend, frontend, or migration code was modified for this review.

## Multi-Tenant Verdict

```text
GO WITH FIXES for private pilot.
NO GO for public SaaS launch until platform identity and operational blockers
are addressed.
```

## Architecture Classification

ALRSCRM uses:

```text
Shared Database / Shared Schema
```

Tenant boundary:

```text
organization_id
```

Operational branch boundary:

```text
branch_id
```

The architecture is valid for SaaS if every query, metric, report, background
task, audit event, and public workflow consistently applies tenant scope.

## Tenant Isolation Strengths

| Area | Status | Evidence |
| --- | --- | --- |
| Tenant-aware login | Strong | `backend/app/auth/service.py` looks up organization code before user lookup. |
| Duplicate emails | Supported | User lookup is scoped by `organization_id + email`. |
| JWT claims | Implemented | Access and refresh tokens include organization and branch claims. |
| Domain models | Broadly implemented | Domain tables include `organization_id` and usually `branch_id`. |
| Service authorization | Broadly implemented | Services use `AuthorizationContext` and branch checks. |
| Public Gallery | Hardened | Token-based access replaces UUID public secret. |
| Public Delivery | Hardened | Delivery token, password, session, and signed URL controls exist. |
| Finance | Scoped | Finance invoices/payments/settings are tenant and branch scoped. |
| Integrations | Scoped | Integration records store organization and optional branch scope. |

## Multi-Tenant Findings

| Severity | Finding | Evidence | Recommendation |
| --- | --- | --- | --- |
| HIGH | Platform Super Admin is still represented as a tenant user in pseudo organization `ALRSCRM`. | `docs/PLATFORM_VS_TENANT_ARCHITECTURE_REVIEW.md`, `backend/scripts/seed_super_admin.py` | Introduce platform-scoped identity before broad SaaS scale. |
| HIGH | Some nullable unique constraints do not enforce organization-level uniqueness in PostgreSQL. | Finance and integrations migrations | Add partial unique indexes for `branch_id IS NULL` cases. |
| HIGH | Finance numbering uses sequence-backed numbers, but tenant/branch independent sequence requirements need final verification. | `backend/alembic/versions/202606100017_create_finance_mvp.py` | Implement or document independent invoice/payment sequences per tenant/branch. |
| MEDIUM | Platform and tenant RBAC share the same user/role model. | `backend/app/identity/policies.py`, `backend/app/identity/seeds.py` | Split platform permissions from tenant permissions in a future sprint. |
| MEDIUM | Audit logs are tenant-scoped but platform audit semantics are not yet first-class. | `backend/app/shared/models/audit_log.py` | Add `actor_scope` or platform audit model during platform identity separation. |
| MEDIUM | Background and scheduled operations need an explicit tenant-aware worker pattern. | Sales aging, Delivery artifact generation | Add job table/queue with organization and branch columns on all jobs. |
| MEDIUM | Tenant-owned integrations can be organization-wide or branch-specific, but the product policy for override/precedence is not fully documented. | `backend/app/integrations/models/integration.py` | Define whether branch integrations override organization integrations. |
| LOW | Frontend route visibility is permission-driven but not a security boundary. | `frontend/src/routes/routePermissions.ts` | Continue testing backend authorization as source of truth. |

## Module Isolation Matrix

| Module | Tenant Scope | Branch Scope | Notes |
| --- | --- | --- | --- |
| Identity | Yes | Partial | Users belong to organizations; branch can be nullable for broader roles. |
| Organizations | Platform managed | Not applicable | Current Super Admin still uses pseudo tenant. |
| Branches | Yes | Entity itself | Branches belong to organizations. |
| Families | Yes | Yes | Family aggregate is tenant and branch scoped. |
| Sales | Yes | Yes | Opportunity and follow-up workflows are scoped; read-time aging should move to jobs. |
| Bookings | Yes | Yes | Package, booking, schedule, and assignment flows are scoped. |
| Galleries | Yes | Yes | Public token flows resolve back to tenant-scoped Gallery. |
| Editing | Yes | Yes | EditingJob references tenant and branch scope. |
| Delivery | Yes | Yes | DeliveryJob and public artifacts are tenant scoped. |
| Finance | Yes | Yes | Finance source of truth is separate from Booking snapshots. |
| Integrations | Yes | Optional | Organization-wide and branch-specific integrations are supported. |

## Branch Boundary Review

Branch scoping is designed as an operational permission boundary, not a tenant
boundary. Branch Manager users should see only branch data. Organization Admins
and Owners can operate across branches in their organization.

Production concerns:

- Every report and metric must accept branch filters or respect branch-scoped
  caller context.
- Organization-wide settings and integrations must be distinguished from
  branch-specific records in both UI and backend constraints.
- Nullable `branch_id` uniqueness needs database-level protection.

## Platform Boundary Review

The biggest remaining SaaS architecture issue is platform identity.

Current state:

```text
Organization: ALRSCRM
Branch: Platform
User: admin@admin.com
Role: Super Admin
```

This works operationally, but it means platform administration is modeled as
tenant administration with an `is_platform` role bypass.

Recommended target:

```text
Platform user: admin@admin.com
Tenant organizations: customer/studio organizations only
Tenant owner: owns each tenant
```

Do not remove `ALRSCRM` immediately. The current schema, login, JWT claims, and
authorization context assume every authenticated user has an organization.

## Finance Multi-Tenant Review

Finance is correctly separated from operational domains. Invoices and payments
should remain the financial source of truth. Booking totals should remain
compatibility snapshots only.

Production concerns:

- Invoice and payment sequences should be independent per tenant and, if
  required by business policy, per branch.
- FinanceSettings must be unique for organization-wide scope and branch scope.
- Reports must never aggregate across organizations for tenant users.
- Platform finance should remain separate from tenant studio finance.

## Integrations Multi-Tenant Review

Integrations are tenant-owned and optionally branch-owned.

Production concerns:

- Organization-wide integrations with `branch_id = NULL` need database-level
  uniqueness.
- Branch override behavior should be documented.
- Provider verification must be real before health dashboards are trusted.
- Credential decryption should happen only inside provider-specific service
  boundaries.

## Required Pre-Launch Multi-Tenant Tests

- Duplicate email can log into the correct organization only.
- Tenant user cannot read another tenant's Families, Sales, Bookings,
  Galleries, Editing, Delivery, Finance, or Integrations.
- Branch Manager cannot read another branch's scoped records.
- Organization Admin can read all branch records within the same organization.
- Platform Super Admin can onboard tenants but does not accidentally create
  operational tenant records in customer domains.
- Public Gallery token cannot resolve another tenant's Gallery.
- Public Delivery token cannot resolve another tenant's DeliveryJob.
- Finance metrics cannot include another tenant's invoices/payments.
- Integration health cannot include another tenant's integrations.

## Multi-Tenant Launch Decision

```text
GO WITH FIXES for controlled private pilot.
NO GO for open SaaS launch until platform identity separation, nullable unique
constraints, and operational tenant tests are complete.
```
