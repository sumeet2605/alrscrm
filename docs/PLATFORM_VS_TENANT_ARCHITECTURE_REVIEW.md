# Platform Vs Tenant Architecture Review

Review scope:

- Sprint 8 SaaS organization onboarding
- Current Sprint 8.1 tenant-aware login and bootstrap behavior
- Identity, RBAC, organization, branch, onboarding, and bootstrap code

No code changes were made as part of this review.

## Executive Summary

The current implementation is operational, but the platform layer and tenant
layer are not cleanly separated.

Today, the platform Super Admin is modeled as a normal `users` row inside a
pseudo-tenant organization:

```text
Organization: ALRSCRM
Branch: Platform
User: admin@admin.com
Role: Super Admin
```

Platform authority comes from `Role.is_platform = true`, not from a separate
platform identity boundary.

This works with the current schema because `users.organization_id` is required
and login requires `organization_code + email + password`. It is not the ideal
long-term SaaS architecture because `ALRSCRM` is not a real customer tenant and
`Platform` is not a real studio branch.

Recommendation:

```text
NO-GO for immediately removing the ALRSCRM organization.
GO for a planned migration to platform-scoped Super Admin identity.
```

## Direct Answers

| Question | Answer |
| --- | --- |
| Should Super Admin belong to an organization? | Long term, no. Super Admin should be platform-scoped. In the current implementation, yes, because the schema and login flow require it. |
| Should ALRSCRM exist as an organization? | Long term, no, not as a tenant organization. It currently exists as a compatibility/pseudo-platform tenant. |
| Should platform administration be separate from tenant organizations? | Yes. Platform administration should be a separate boundary that manages tenants without belonging to one. |
| Should organization ownership be assigned to tenant Owner users instead of Super Admin? | Yes. Super Admin should create/onboard tenants; tenant Owner users should own tenant operations. |
| Do current RBAC and login flows assume a platform organization? | Yes. Bootstrap, login, JWT claims, and `AuthorizationContext` all assume the Super Admin has an organization context. |

## Current Architecture Diagram

```text
Shared Database / Shared Schema
└── organizations
    ├── ALRSCRM
    │   ├── organization_settings
    │   ├── Branch: Platform
    │   │   └── User: admin@admin.com
    │   │       └── Role: Super Admin
    │   │           └── is_platform = true
    │   └── Used as platform login tenant
    │
    └── Alluring Lens Studios
        ├── organization_settings
        ├── Branch: Main Studio
        │   └── Owner / tenant users
        └── Families, Sales, Bookings, Galleries, Editing, Delivery
```

Current platform behavior:

- `seed_super_admin.py` creates `ALRSCRM`, `Platform`, and `admin@admin.com`.
- `User.organization_id` is non-null.
- `User.branch_id` is optional, but bootstrap assigns the Platform branch.
- Login requires a real `Organization.code`.
- Access tokens include `organization_id` and `branch_id`.
- `AuthorizationContext.from_user()` requires `user.organization_id`.
- Platform permission bypass comes from `context.is_platform_admin`.

## Recommended Architecture Diagram

```text
Shared Database / Shared Schema
├── platform_users
│   └── admin@admin.com
│       └── Platform roles / permissions
│
├── platform_audit
│   └── Platform administrative events
│
└── tenant organizations
    ├── Organization: Alluring Lens Studios
    │   ├── Owner user
    │   ├── Branch: Main Studio
    │   ├── Tenant RBAC
    │   └── Families, Sales, Bookings, Galleries, Editing, Delivery
    │
    └── Organization: Future tenant
        ├── Owner user
        ├── Branches
        └── Tenant domain data
```

Recommended platform behavior:

- Platform Super Admin is not a member of any tenant organization.
- Platform login does not require a tenant organization code.
- Tenant login continues to require `organization_code + email + password`.
- Tenant Owner users own tenant setup and operations.
- Platform users manage organizations but do not become organization owners.
- Platform audit events are distinguishable from tenant audit events.

## Evidence From Implementation

### Bootstrap

`backend/scripts/seed_super_admin.py` defines and creates:

- `PLATFORM_ORGANIZATION_CODE = "ALRSCRM"`
- `PLATFORM_ORGANIZATION_NAME = "ALRSCRM"`
- `PLATFORM_BRANCH_CODE = "PLATFORM"`
- `PLATFORM_BRANCH_NAME = "Platform"`
- `ADMIN_EMAIL = "admin@admin.com"`

The script creates an organization, branch, and Super Admin user in that
organization. Optional sample tenant creation is separate and creates:

- Organization: `Alluring Lens Studios`
- Branch: `Main Studio`
- Owner user: `owner@alluringlens.com`

### User Model

`backend/app/identity/models/user.py` requires:

```text
organization_id nullable=False
UniqueConstraint(organization_id, email)
```

This means the current identity model cannot represent a platform user outside
an organization.

### Organization Model

`backend/app/identity/models/organization.py` has no organization type or
platform discriminator. `ALRSCRM` and real tenant organizations are stored in
the same table with the same shape.

### Login Flow

`backend/app/auth/service.py` authenticates by:

```text
organization_code -> active Organization -> user by organization_id + email
```

Token claims are created from the user:

```text
organization_id = user.organization_id
branch_id = user.branch_id
```

This makes `ALRSCRM` part of the login contract for the platform Super Admin.

### RBAC

`backend/app/identity/seeds.py` marks `Super Admin` as:

```text
is_platform = true
```

`backend/app/identity/policies.py` then allows platform bypass through:

```text
context.is_platform_admin
```

The authority model is platform-aware, but the identity storage model is still
tenant-shaped.

### Organization Onboarding

`backend/app/identity/services/organization_service.py` allows onboarding only
when:

```text
context.is_platform_admin
```

It creates the tenant organization, default branch, and tenant Owner user. This
is directionally correct, but the platform actor is still a user inside
`ALRSCRM`.

## Required Database Changes

There are two viable designs.

### Recommended: Separate Platform Identity

Add a dedicated platform identity boundary:

- `platform_users`
- `platform_user_roles` or platform-specific role assignments
- Optional `platform_audit_logs`, or extend `audit_logs` with `actor_scope`

Keep tenant users unchanged:

- `users.organization_id` remains required for tenant users.
- `users.branch_id` remains tenant operational scope.
- Tenant email uniqueness remains `(organization_id, email)`.

Benefits:

- Cleanest platform/tenant separation.
- No nullable tenant foreign keys for platform users.
- Fewer accidental cross-tenant assumptions.
- Clearer auth, audit, and product behavior.

Costs:

- Requires separate platform auth handling.
- Requires platform-specific current-user dependency.
- Requires frontend platform login/session support.

### Alternative: Single User Table With Scope

Modify `users`:

- Add `account_scope`, for example `PLATFORM` or `TENANT`.
- Make `organization_id` nullable for platform users.
- Make `branch_id` nullable for platform users.
- Replace or supplement `uq_user_org_email`.

Suggested constraints:

```text
Tenant users: organization_id is not null
Platform users: organization_id is null
Tenant email uniqueness: unique (organization_id, email)
Platform email uniqueness: unique (email) where account_scope = PLATFORM
```

Benefits:

- Smaller table footprint.
- Reuses more existing user/RBAC code.

Costs:

- More conditional logic in every identity, RBAC, and audit path.
- Higher risk of tenant queries accidentally including platform users.

### Transitional Option: Organization Type

Add `organizations.kind`:

```text
PLATFORM
TENANT
```

Mark `ALRSCRM` as `PLATFORM`.

This is useful as a compatibility bridge but does not fully separate platform
identity from tenant identity. It still keeps Super Admin inside an
organization-shaped record.

## Required RBAC Changes

Recommended RBAC model:

- Platform roles are separate from tenant roles.
- `Super Admin` is a platform role only.
- Tenant roles remain:
  - Owner
  - Organization Admin
  - Branch Manager
  - Sales Executive
  - Photographer
  - Editor
  - Customer Success
  - Client

Required policy changes:

- `AuthorizationContext` must support platform context without
  `organization_id`.
- Platform-only permissions should be evaluated separately from tenant
  permissions.
- Platform routes should require platform context.
- Tenant routes should require tenant context.
- Platform admins should not satisfy tenant-scoped route access by carrying a
  fake branch.

Recommended platform permissions:

- `platform:organizations:view`
- `platform:organizations:create`
- `platform:organizations:update`
- `platform:organizations:deactivate`
- `platform:organizations:onboard`
- `platform:audit:view`
- `platform:users:manage`
- `platform:settings:manage`

Existing `organizations:*` permissions can be retained temporarily as aliases
for backward compatibility.

## Required Onboarding Changes

Bootstrap should create:

```text
Platform Super Admin
```

It should not create:

```text
Organization: ALRSCRM
Branch: Platform
```

Tenant onboarding should create:

```text
Organization
Default Branch
Tenant Owner user
Organization Settings
```

Ownership rule:

- Super Admin is the creator/onboarding actor.
- Tenant Owner is the organization owner.
- Super Admin is not assigned as a tenant user by default.

Recommended login model:

```text
Tenant login:
organization_code + email + password

Platform login:
email + password
```

A compatibility alternative is to temporarily accept:

```text
organization_code = ALRSCRM
```

and internally route it to platform login until operators migrate.

## Migration Strategy From Current Model

### Step 1: Add Platform Identity Without Removing ALRSCRM

- Add platform identity storage.
- Create a platform admin record for `admin@admin.com`.
- Keep existing `ALRSCRM` organization and user active during transition.
- Add tests for platform login and tenant login.

### Step 2: Add Platform Authentication Path

- Add platform login endpoint or extend login with explicit platform mode.
- Issue platform JWTs without tenant `organization_id` and `branch_id` claims,
  or include a clear `scope = PLATFORM` claim.
- Keep tenant JWTs unchanged.

### Step 3: Split Authorization Contexts

- Introduce platform context and tenant context.
- Require platform context for organization onboarding and platform admin APIs.
- Require tenant context for domain APIs such as families, sales, bookings,
  galleries, editing, and delivery.

### Step 4: Move Super Admin Off The Pseudo-Tenant

- Stop using the `ALRSCRM` user for new platform sessions.
- Preserve the old user row temporarily for audit history and rollback.
- Mark the old `ALRSCRM` organization as internal or inactive only after route
  and login compatibility is complete.

### Step 5: Hide Or Retire ALRSCRM

Options:

- Mark `ALRSCRM` as internal/platform and hide it from organization lists.
- Keep it as a legacy tombstone for historical audit references.
- Remove it only after all foreign key dependencies and audit requirements are
  resolved.

Immediate hard delete is not recommended.

## Risks

### Login Risk

Removing `ALRSCRM` immediately would break current Super Admin login because
authentication requires an active `Organization.code`.

### Schema Risk

`users.organization_id` is non-null. Platform-scoped users cannot exist until
the schema is changed or a separate platform user table is added.

### Authorization Risk

`AuthorizationContext` currently includes a required `organization_id`. Making
platform users organization-less requires careful route dependency changes.

### JWT Compatibility Risk

Current tokens include tenant claims. Platform tokens need a different shape or
a clear scope claim. Frontend and backend guards must handle both.

### Audit Risk

Recent audit hardening added tenant scope. Platform audit events need explicit
platform semantics so they are not incorrectly attributed to `ALRSCRM`.

### Frontend Risk

The frontend currently treats authenticated users uniformly. Platform
navigation and tenant navigation should be separated to avoid showing tenant
workflows in platform sessions.

### Data Migration Risk

Existing databases may already contain:

- `ALRSCRM`
- `Platform` branch
- `admin@admin.com`
- Audit rows tied to those IDs

Those references must be preserved or migrated without breaking history.

## Backward Compatibility Concerns

Recommended compatibility behavior:

- Keep `ALRSCRM` login working for one release after introducing platform login.
- Show a migration warning or documentation for platform operators.
- Keep existing Super Admin role and permissions until platform roles are fully
  introduced.
- Preserve `organization_id` and `branch_id` in old audit rows.
- Do not remove existing `ALRSCRM` foreign key targets until historical records
  are no longer dependent on them.

## Recommended Target State

Target state:

- Platform identity is separate from tenant identity.
- Super Admin is platform-scoped only.
- `ALRSCRM` is not a tenant organization.
- Tenant organizations are customer/studio organizations only.
- Tenant Owner users own tenant operations.
- Platform admins onboard and administer tenants without being tenant members.
- Tenant login remains organization-code aware.
- Platform login is separate and does not require a tenant code.

## GO / NO-GO Recommendation

```text
NO-GO for immediately removing ALRSCRM and making Super Admin platform-scoped
only in the current codebase.
```

Reason:

- Current schema requires `users.organization_id`.
- Current login requires a real active `Organization.code`.
- Current JWT claims and authorization context assume organization scope.
- Bootstrap currently creates and depends on the pseudo-platform organization.

```text
GO for a planned migration to remove ALRSCRM as a platform tenant and introduce
platform-scoped Super Admin identity.
```

Recommended sprint:

```text
Sprint 8.2 or Sprint 9: Platform Identity Separation
```

The work should be treated as an architecture migration, not a small cleanup.
The safest approach is to introduce platform identity alongside the existing
model, migrate Super Admin authentication, then retire `ALRSCRM` after backward
compatibility is proven.
