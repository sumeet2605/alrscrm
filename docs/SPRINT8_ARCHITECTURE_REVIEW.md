# Sprint 8 Architecture Review

Sprint 8 scope:

- SaaS Organization Onboarding
- Organization Management UI
- Organization Settings
- Platform bootstrap correction
- Tenant-aware login design documentation only

This review was completed before implementation.

## Existing Architecture Baseline

ALRSCRM currently uses:

```text
Shared Database
Shared Schema
Tenant boundary: organization_id
Branch boundary: branch_id
```

This remains the correct architecture for Sprint 8. Sprint 8 must not introduce
separate schemas or separate databases per tenant.

## Platform Versus Customer Tenant Boundary

The platform organization is:

```text
ALRSCRM
```

Purpose:

- Platform administration
- SaaS operations
- Support
- Future billing
- Future feature flags
- Future global settings

Customer organizations are normal tenants:

- Alluring Lens Studios
- Little Smiles Photography
- Baby Moments Studio
- Newborn Stories

Important rule:

```text
Alluring Lens Studios must not be hardcoded as the platform tenant or default
runtime tenant.
```

It may be seeded only as optional sample data when explicitly enabled.

## Aggregate Boundary Validation

### Organization Aggregate

`Organization` is the tenant aggregate root.

It owns:

- Organization identity
- Organization active state
- Organization settings
- Branches
- Tenant user membership

It does not own:

- Platform authentication tokens
- Families
- Opportunities
- Bookings
- Galleries
- Editing jobs
- Delivery jobs

Those aggregates reference `organization_id`.

### Organization Settings

`OrganizationSettings` is an Organization-owned entity.

It belongs inside the Organization aggregate because settings have no useful
lifecycle outside an Organization and should be created at onboarding time.

Settings fields:

- Studio name
- Logo URL
- Contact email
- Contact phone
- Website
- Address
- Timezone
- Currency
- Delivery expiry default
- Gallery selection default limit

### Branch Boundary

`Branch` remains an Organization-owned entity.

Onboarding creates one default branch in the same transaction as Organization
creation.

### Owner User Boundary

`User` remains an Identity aggregate/entity linked to Organization and optional
Branch.

Onboarding may create the first tenant Owner, but the Owner user does not become
part of the Organization aggregate in the domain model. It is created in the
same application transaction for onboarding consistency.

### Existing Sprint Boundaries

Sprint 8 must preserve these boundaries:

| Sprint | Aggregate | Sprint 8 Rule |
| --- | --- | --- |
| Sprint 1 | Identity and Access | Add organization onboarding without weakening RBAC. |
| Sprint 2 | Family | Families continue to reference customer organization and branch. |
| Sprint 3 | Opportunity | Opportunities continue to reference Family and Organization. |
| Sprint 4 | Booking | Bookings continue to reference Family, Opportunity, Organization, and Branch. |
| Sprint 5 | Gallery | Galleries continue to reference Booking, Organization, and Branch. |
| Sprint 6 | EditingJob | Editing jobs continue to reference Gallery, Booking, Organization, and Branch. |
| Sprint 7 | DeliveryJob | Delivery jobs continue to reference EditingJob, Organization, and Branch. |

No Sprint 8 workflow should create Families, Opportunities, Bookings,
Galleries, Editing jobs, or Delivery jobs.

## Onboarding Transaction

The onboarding command must create these records in one transaction:

1. Organization
2. OrganizationSettings
3. Default Branch
4. Owner User
5. Owner role assignment

Rollback rule:

```text
If any step fails, none of the records should remain committed.
```

This must be implemented as an application service method, not as multiple
frontend calls.

## RBAC Decision

New permissions:

- `organizations:view`
- `organizations:create`
- `organizations:update`
- `organizations:deactivate`
- `organizations:onboard`

Only `Super Admin` receives organization creation and onboarding permissions.

`Organization Admin` must not be able to create tenants.

Existing `identity:organizations:*` permissions may remain for backward
compatibility, but Sprint 8 routes should enforce the new organization
permissions.

## Route Design

Backend routes:

- `GET /api/v1/organizations`
- `POST /api/v1/organizations`
- `GET /api/v1/organizations/{organization_id}`
- `PATCH /api/v1/organizations/{organization_id}`
- `POST /api/v1/organizations/{organization_id}/activate`
- `POST /api/v1/organizations/{organization_id}/deactivate`
- `POST /api/v1/organizations/onboard`
- `GET /api/v1/organizations/{organization_id}/settings`
- `PATCH /api/v1/organizations/{organization_id}/settings`

Frontend routes:

- `/organizations`
- `/organizations/new`
- `/organizations/:id`
- `/organizations/:id/settings`

## Tenant Isolation Requirements

Organization onboarding is a platform operation.

Rules:

- Only platform Super Admin can onboard tenants.
- Customer organizations must never see other organizations.
- Organization Admin cannot create or onboard tenants.
- Created Owner must belong to the newly created organization.
- Created default Branch must belong to the newly created organization.
- All existing modules continue to scope data by `organization_id` and
  `branch_id`.

## Bootstrap Strategy

Platform bootstrap must create:

```text
Organization: ALRSCRM
Branch: Platform
Super Admin: admin@admin.com
```

Optional sample tenant seed:

```text
SEED_SAMPLE_TENANT=true
```

When enabled, seed:

```text
Organization: Alluring Lens Studios
Branch: Main Studio
Owner: owner@alluringlens.com
```

All bootstrap behavior must be idempotent.

## Tenant-Aware Login

Sprint 8 must not implement login changes.

It must document options:

- Global unique email
- Organization code + email
- Subdomain based login
- Custom domain login

The current implementation allows tenant-local email uniqueness but login looks
up users by email alone. That design gap should be documented and resolved in a
future authentication sprint.

## Event Ownership

Sprint 8 should remain audit-backed. No outbox or event bus is introduced.

Audit events to record:

- `organization.created`
- `organization.updated`
- `organization.activated`
- `organization.deactivated`
- `organization.onboarded`
- `organization.settings_updated`

These are audit events, not asynchronous integration events.

## Non-Goals

Sprint 8 must not implement:

- Payments
- Subscriptions
- Public self-signup
- Tenant-aware login changes
- Separate tenant databases
- Separate tenant schemas
- Feature flags
- Billing

## Implementation Risk Review

| Risk | Mitigation |
| --- | --- |
| Accidentally treating Alluring Lens Studios as platform tenant | Keep ALRSCRM as platform bootstrap and gate sample tenant behind `SEED_SAMPLE_TENANT`. |
| Partial onboarding records | Use one backend transaction. |
| Organization Admin tenant creation | Enforce `context.is_platform_admin` and new permissions. |
| Breaking existing organization APIs | Keep CRUD routes backward compatible. |
| Frontend route exposure to tenant admins | Route permissions Super Admin only. |
| Duplicate owner email ambiguity | Keep current behavior for Sprint 8 and document tenant-aware login design. |

## Architecture Verdict

```text
GO
```

Sprint 8 is compatible with the existing Sprint 1-7.1 architecture if it is
implemented as platform-admin-only organization onboarding, keeps shared
database/shared schema tenancy, and treats Alluring Lens Studios only as an
optional sample customer tenant.

