# Organization Onboarding Gap Analysis

Reviewed against the current frontend and backend implementation on
`development`.

No code changes were made as part of this review.

## Executive Summary

The backend has organization CRUD APIs, and a platform Super Admin can create an
organization through the API. The frontend does not expose organization
management, organization onboarding, or a setup wizard.

ALRSCRM currently supports manually managed organizations better than it
supports SaaS onboarding.

## Direct Answers

| Question | Answer |
| --- | --- |
| Can a new organization currently be created? | Yes, through the backend API by a platform Super Admin. |
| Is there a backend API for organization creation? | Yes, `POST /api/v1/organizations`. |
| Is there a frontend screen for organization creation? | No. |
| Is there a frontend workflow for onboarding a new organization? | No. |
| Can a Super Admin create organizations? | Backend yes; frontend has no organization UI. |
| Can an Organization Admin create organizations? | No. The service blocks non-platform admins. |
| Is there an organization setup wizard? | No. |
| What is missing to support SaaS onboarding? | Organization UI, setup wizard, default branch creation, owner creation, tenant-aware login, invite flow, settings, and tests. |

## Backend Findings

### Organization API Exists

The backend exposes:

- `GET /api/v1/organizations`
- `POST /api/v1/organizations`
- `GET /api/v1/organizations/{organization_id}`
- `PATCH /api/v1/organizations/{organization_id}`
- `DELETE /api/v1/organizations/{organization_id}`

Routes require identity organization permissions.

### Super Admin Creation Is Supported

`organization_service.create_organization()` allows creation only when the
caller is a platform admin.

Platform admin behavior comes from the `Super Admin` role, where
`role.is_platform` is true.

### Organization Admin Creation Is Blocked

Although `Organization Admin` has broad permissions in the seed definitions, the
service-level guard prevents non-platform admins from creating organizations.

This is the correct boundary for SaaS tenant creation.

### Branch And User APIs Exist

The backend supports:

- Creating branches
- Creating users
- Assigning roles
- Branch-scoped and organization-scoped access control

However, these APIs are not composed into an onboarding transaction.

## Frontend Findings

### No Organization API Adapter

`frontend/src/api/identity.ts` exposes:

- Branch APIs
- User APIs
- Role APIs

It does not expose:

- `listOrganizations`
- `createOrganization`
- `updateOrganization`
- `deactivateOrganization`

Generated OpenAPI types contain organization contracts, but the manual API
adapter does not use them.

### No Organization Route

Frontend routes include Branches, Users, Roles, Families, Sales, Bookings,
Galleries, Production, and Delivery routes.

No route exists for:

- `/organizations`
- `/organizations/new`
- `/onboarding`
- `/setup`
- `/tenant-setup`

### No Navigation Entry

Dashboard navigation does not include Organization Management.

### No Setup Wizard

No frontend module implements:

- Organization details
- Default branch setup
- Owner/admin user setup
- Initial role assignment
- First-login tenant setup

## Default Bootstrap Findings

The development bootstrap script creates a platform admin and a default
organization, but not a full onboarding setup.

Current script:

- `backend/scripts/seed_super_admin.py`

Current behavior:

- Creates organization code `ALRS`
- Creates organization name `ALRSCRM`
- Creates or updates `admin@admin.com`
- Assigns `Super Admin`
- Does not create a default branch
- Does not create an Owner user

Production Docker startup does not run `seed_super_admin.py`.

## SaaS Onboarding Gaps

| Gap | Current State | Required State |
| --- | --- | --- |
| Organization management frontend | Missing | Super Admin organization list/create/edit/deactivate UI |
| Onboarding wizard | Missing | Guided create organization, branch, owner, and settings flow |
| Default branch creation | Manual | Automatic during onboarding |
| Owner user creation | Manual | Created or invited during onboarding |
| Tenant-aware login | Missing | Login identifies tenant via org code, subdomain, domain, or equivalent |
| Organization settings | Missing | Studio profile, timezone, contact, storage, delivery, and branding settings |
| Invitation flow | Missing | Secure owner/admin invite and password setup |
| Bootstrap consistency | Dev-only default super admin | Production-safe idempotent bootstrap path |
| Tenant test coverage | Partial | End-to-end onboarding and duplicate email tenant tests |

## Product Gaps

The current product can be operated by a technical/admin user, but SaaS
onboarding needs a productized flow:

1. Super Admin opens Organization Management.
2. Super Admin creates a new organization.
3. System creates the default branch.
4. System creates or invites the organization owner.
5. Owner signs in and completes organization setup.
6. Owner creates users and branch managers.
7. Tenant data remains isolated from all other organizations.

## Security Gaps

Tenant onboarding should not be added as a simple public signup until these
security decisions are made:

- Whether organizations are created only by platform Super Admins or through
  public signup.
- Whether login uses organization code, domain, subdomain, or global username.
- Whether duplicate emails across organizations are supported in the login UX.
- Whether initial owner credentials are emailed, set by invite, or generated
  with one-time token.
- Whether public Gallery sharing is hardened before exposing broader SaaS use.

## Recommended Implementation

### Sprint Recommendation

Implement in two steps:

1. Sprint 7.2: Default organization bootstrap for `Alluring Lens Studios`.
2. Sprint 8: SaaS Organization Onboarding module.

### Sprint 7.2 Scope

- Idempotent default organization bootstrap.
- Idempotent default branch bootstrap.
- Link Super Admin to the default organization.
- Create or prepare an Owner user according to environment variables.
- Add tests for idempotency and branch creation.

### Sprint 8 Scope

- Organization Management page for Super Admin.
- Organization create/edit/deactivate workflows.
- Default branch creation workflow.
- Owner invite/create workflow.
- Tenant-aware login decision and implementation.
- Onboarding tests across backend and frontend.

## Estimated Effort

| Work | Estimate |
| --- | --- |
| Default organization bootstrap | 1-2 engineering days |
| Backend onboarding service | 2-3 engineering days |
| Frontend organization management | 3-5 engineering days |
| Tenant-aware login design and implementation | 3-5 engineering days |
| Tests and documentation | 2-3 engineering days |

## Recommendation

```text
GO for adding Super Admin driven organization onboarding.
NO-GO for public self-service signup until tenant-aware login and security
flows are designed.
```

