# Multi-Tenant Review

Reviewed against the current implementation on `development`.

Scope reviewed:

- Backend models, migrations, routes, services, repositories, seeds, and tests
- Frontend routes, API adapters, generated OpenAPI types, and navigation
- Docker startup behavior and bootstrap scripts

No code changes were made as part of this review.

## Executive Answer

ALRSCRM is implemented as a multi-organization SaaS application using a shared
database and shared schema.

Tenant boundary:

```text
organization_id
```

Branch boundary:

```text
branch_id
```

The main business modules generally enforce tenant and branch isolation through
service-layer scope checks and repository filters. The implementation is not yet
a fully complete SaaS onboarding platform because organization onboarding is
not exposed in the frontend and authentication is not tenant-aware when duplicate
emails exist across organizations.

## Architecture Type

Current architecture:

```text
Shared Database, Shared Schema
```

Evidence:

- `docker-compose.yml` defines one PostgreSQL database service using
  `POSTGRES_DB: alrscrm`.
- Alembic migrations create all tenant data in one shared schema.
- Domain tables carry `organization_id` and usually `branch_id` columns.
- Service and repository methods apply organization and branch filters instead
  of switching schemas or databases.

Not implemented:

- Shared database, separate schema per tenant
- Separate database per tenant

## Tenant And Branch Boundary Evidence

| Area | Evidence |
| --- | --- |
| Tenant model | `organizations` table is the tenant root. |
| Branch model | `branches.organization_id` links branches to tenants. |
| User model | `users.organization_id`, optional `users.branch_id`, and composite branch/organization FK. |
| Family model | `families.organization_id` and `families.branch_id`. |
| Sales model | Opportunities carry `organization_id` and `branch_id`. |
| Booking model | Bookings, packages, and addons carry `organization_id` and `branch_id`. |
| Gallery model | Galleries and upgrade requests carry tenant and branch context. |
| Editing model | Editing jobs carry tenant and branch context. |
| Delivery model | Delivery jobs, audits, and access workflows preserve tenant and branch context. |

## Modules That Enforce Tenant Isolation

### Identity

Identity is tenant-aware.

Evidence:

- `Organization` is the tenant root.
- `Branch` has `organization_id` and unique `(organization_id, code)`.
- `User` has `organization_id`, optional `branch_id`, unique
  `(organization_id, email)`, and composite branch/organization FK.
- `organization_service.list_organizations()` limits non-platform users to
  their own organization.
- `branch_service` limits non-platform users to their own organization and
  branch-scoped users to their own branch.
- `user_service` limits users by organization and branch scope.
- Tests cover owner visibility and cross-organization branch assignment.

### Family

Family APIs are tenant-aware.

Evidence:

- `Family` stores `organization_id` and `branch_id`.
- Repositories support organization and branch filters.
- Services validate family organization and branch against the caller scope.
- Branch-scoped users are forced to their own branch.

Risk:

- `primary_contact_phone` is globally unique. This protects duplicate records
  globally but is restrictive for multi-tenant SaaS because two unrelated
  organizations cannot register the same phone number.

### Sales

Sales APIs are tenant-aware.

Evidence:

- `Opportunity` stores `organization_id`, `branch_id`, and `family_id`.
- Opportunity repositories filter by organization and branch.
- Follow-up queries are scoped through the parent Opportunity.
- Overdue follow-up aging now receives organization and branch scope.
- Tests cover cross-tenant and cross-branch overdue follow-up aging.

Reference data note:

- `LostReason` is global database-driven reference data. That is acceptable for
  the current implementation, but it is not tenant-customizable.

### Bookings

Booking APIs are tenant-aware.

Evidence:

- Bookings, packages, package addons, booking items, schedules, and assignments
  are reached through tenant-scoped services.
- Packages and addons are branch-specific.
- Booking creation validates Family and Opportunity consistency.
- Photographer access is narrowed to assigned work.

Scalability note:

- Booking number generation should be reviewed for concurrency and tenant
  formatting as usage grows.

### Galleries

Staff gallery APIs are tenant-aware.

Evidence:

- Gallery list, metrics, update, upload, and staff details use organization and
  branch scope.
- Gallery upgrade requests include organization and branch fields and are
  branch-scoped.
- Storage paths include organization and branch identifiers.

Public gallery access is weaker than delivery access.

Risk:

- Public gallery routes are UUID-based and can expose galleries to anyone with
  the UUID if the gallery has no password and is not expired.
- Public favorite mutation is available through public gallery routes.
- Delivery has opaque token hardening; Gallery public access has not yet been
  hardened to that level.
- `authenticate_public_gallery()` should be reviewed because the expiry check is
  not applied on the normal authentication path.

### Editing

Editing APIs are tenant-aware.

Evidence:

- `EditingJob` carries organization and branch context.
- Editing creation from Gallery copies tenant and branch context.
- Editing queries and metrics use organization and branch filters.
- Editor views are additionally limited to assigned editor work.
- Tests cover cross-tenant editing job access.

### Delivery

Delivery APIs are tenant-aware and the strongest public-access implementation.

Evidence:

- `DeliveryJob` carries organization and branch context.
- Staff delivery list, detail, metrics, update, and lifecycle workflows are
  scoped by organization and branch.
- Public delivery access uses opaque tokens, token hashing, expiry, revocation,
  and delivery session tokens.
- Delivery audits carry tenant and branch columns.
- Tests cover tenant and branch scoped delivery access.

## Modules Or Paths With Tenant Risks

### Authentication Login

Risk level: Major.

The user table allows duplicate emails across organizations through unique
constraint `(organization_id, email)`, but login resolves a user by email alone.

Evidence:

- `User` model uses unique `(organization_id, email)`.
- `get_user_by_email()` filters only by normalized email.
- `AuthService.authenticate()` calls `get_user_by_email(db, email)` without
  organization code, tenant slug, or domain context.

Impact:

- If the same email exists in multiple organizations, login is ambiguous.
- Depending on data state, login can fail unexpectedly or require global email
  uniqueness in practice.
- This is not a direct data leak, but it is not a complete multi-tenant login
  design.

Recommended direction:

- Add a tenant-aware login identifier such as organization code, subdomain,
  domain, or global username.
- Keep existing email/password login backward compatible during migration.

### Public Gallery Access

Risk level: Major.

Gallery public access is UUID-based rather than opaque-token based.

Impact:

- Possession of a gallery UUID can grant access to photos when no password is
  configured.
- This is not a staff route tenant-filter bug, but it is a public endpoint
  privacy risk.

Recommended direction:

- Apply the Delivery 7.1 token model to Gallery sharing.
- Use opaque access tokens, hashed token storage, optional password, expiry,
  revocation, and audit records.

### General Audit Log

Risk level: Medium.

The shared `audit_logs` table stores metadata but does not expose first-class
`organization_id` and `branch_id` columns.

Impact:

- Future audit dashboards or reports can accidentally become hard to scope.
- Delivery-specific audits are stronger because tenant and branch columns were
  added there.

Recommended direction:

- Add first-class tenant and branch columns to general audit logs in a future
  migration.
- Keep metadata as supplemental context, not the primary tenant filter.

### Global Uniqueness Constraints

Risk level: Medium.

Some fields are global even though tenant-local uniqueness may be more natural:

- Family primary contact phone
- Username lower-case unique index

Impact:

- Two tenants may be blocked from using the same customer phone or username.
- This does not leak data directly, but it reduces SaaS isolation at the data
  modeling level.

Recommended direction:

- Decide which identifiers are intentionally global.
- Scope customer-facing identifiers by organization unless there is a clear
  platform-level reason not to.

## Missing Tenant Filters

No confirmed staff-facing CRUD, metrics, dashboard, or reporting route was found
that currently leaks business records across organizations when using the normal
route and service layers.

Important caveats:

- Authentication lookup is not tenant-aware.
- Public Gallery routes intentionally bypass staff auth and need stronger share
  security.
- General `audit_logs` lack first-class tenant and branch columns.
- Some repository `get()` methods load by ID first and rely on service-layer
  scope enforcement. This is acceptable only if routes never bypass services.

## Missing Branch Filters

No confirmed staff-facing branch-scoped route was found that leaks records
across branches through the normal route and service layers.

Branch scope is enforced in:

- Branches
- Users
- Families
- Opportunities and follow-ups
- Bookings, schedules, assignments, packages, and addons
- Galleries and upgrade requests
- Editing jobs and editor dashboards
- Delivery jobs and delivery dashboards

Known non-branch-scoped areas:

- Platform admins can intentionally operate globally.
- Organization owners/admins can operate across branches inside their
  organization.
- Public Gallery and public Delivery routes are client-facing token or UUID
  access flows rather than branch-authenticated staff flows.

## Security Risks

| Risk | Severity | Notes |
| --- | --- | --- |
| Tenant-ambiguous email login | Major | Login does not include organization context. |
| Public Gallery UUID sharing | Major | Delivery is token-hardened; Gallery is not. |
| General audit log lacks tenant columns | Medium | Future reports may be difficult to scope safely. |
| Global customer phone uniqueness | Medium | Tenant-independent customers can conflict. |
| Global username uniqueness | Low/Medium | May be intentional for platform login, but should be documented. |

## Test Evidence

Current tests include meaningful tenant and branch coverage:

- `test_owner_cannot_see_other_organization`
- `test_cross_organization_branch_assignment_is_rejected`
- `test_overdue_followup_aging_does_not_cross_tenant`
- `test_overdue_followup_aging_does_not_cross_branch`
- `test_gallery_upgrade_request_is_branch_scoped`
- `test_editing_job_access_is_tenant_scoped`
- `test_delivery_access_is_tenant_scoped_and_editor_is_view_only`

Recommended additional tests:

- Duplicate email across two organizations and tenant-aware login behavior.
- Public Gallery expired authentication behavior.
- Public Gallery opaque-token access once implemented.
- Audit/reporting endpoints when general audit logs are exposed.

## Final Multi-Tenant Verdict

ALRSCRM is mostly multi-tenant at the application data-access layer.

It is not yet a complete SaaS onboarding platform because:

- Frontend organization creation/onboarding is missing.
- Default organization bootstrap is inconsistent between dev and production.
- Login is not tenant-aware when duplicate tenant-local emails exist.
- Public Gallery sharing needs Delivery-style hardening.

Recommendation:

```text
GO for controlled multi-organization internal use.
NO-GO for open self-service SaaS onboarding until tenant-aware login,
organization onboarding, and public Gallery hardening are completed.
```

