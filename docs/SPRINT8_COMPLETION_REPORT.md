# Sprint 8 Completion Report

Sprint 8 implements SaaS Organization Onboarding.

## Completed Scope

- Organization Management frontend module
- Organization Onboarding wizard
- Transactional backend onboarding command
- Organization Settings entity and APIs
- Platform bootstrap correction
- Optional sample tenant seeding
- RBAC permissions for organization management
- Backend onboarding tests
- Frontend organization tests
- Tenant-aware login design documentation

## Backend Files Created

- `backend/alembic/versions/202606100015_create_organization_settings.py`

## Backend Files Updated

- `backend/app/identity/models/organization.py`
- `backend/app/identity/models/__init__.py`
- `backend/app/identity/routes/organizations.py`
- `backend/app/identity/schemas/organization.py`
- `backend/app/identity/schemas/__init__.py`
- `backend/app/identity/seeds.py`
- `backend/app/identity/services/organization_service.py`
- `backend/scripts/seed_super_admin.py`
- `backend/tests/test_identity_api.py`
- `backend/tests/test_seed_super_admin.py`

## Frontend Files Created

- `frontend/src/modules/organizations/OrganizationListPage.tsx`
- `frontend/src/modules/organizations/OrganizationOnboardingPage.tsx`
- `frontend/src/modules/organizations/OrganizationDetailPage.tsx`
- `frontend/src/modules/organizations/OrganizationListPage.test.tsx`
- `frontend/src/modules/organizations/OrganizationOnboardingPage.test.tsx`

## Frontend Files Updated

- `frontend/src/api/identity.ts`
- `frontend/src/types/identity.ts`
- `frontend/src/routes/AppRoutes.tsx`
- `frontend/src/routes/routePermissions.ts`
- `frontend/src/routes/routePermissions.test.ts`
- `frontend/src/layouts/DashboardLayout.tsx`

## Routes Added

- `/organizations`
- `/organizations/new`
- `/organizations/:id`
- `/organizations/:id/settings`

## APIs Added

- `POST /api/v1/organizations/onboard`
- `POST /api/v1/organizations/{organization_id}/activate`
- `POST /api/v1/organizations/{organization_id}/deactivate`
- `GET /api/v1/organizations/{organization_id}/settings`
- `PATCH /api/v1/organizations/{organization_id}/settings`

## RBAC Added

- `organizations:view`
- `organizations:create`
- `organizations:update`
- `organizations:deactivate`
- `organizations:onboard`

Only Super Admin receives the new organization permissions.

## Bootstrap Behavior

Platform bootstrap creates:

- Organization: `ALRSCRM`
- Branch: `Platform`
- Super Admin: `admin@admin.com`

Optional sample tenant:

```text
SEED_SAMPLE_TENANT=true
```

Creates:

- Organization: `Alluring Lens Studios`
- Branch: `Main Studio`
- Owner: `owner@alluringlens.com`

## Non-Goals Preserved

Sprint 8 does not implement:

- Payments
- Subscriptions
- Public self-signup
- Tenant-aware login changes
- Separate tenant databases
- Separate tenant schemas

## Verification Status

Completed:

```text
ruff check backend frontend: passed
ruff format --check backend frontend: passed
python -m pytest backend/tests: passed, 55 tests
npm run lint: passed
npm run test: passed, 32 tests
npm run build: passed
npm run generate:api-types: passed
docker compose up -d --build: passed
docker compose exec api alembic upgrade head: passed
```

Non-blocking warnings:

- Existing frontend Ant Design `act(...)` warning.
- Existing frontend bundle-size warning.
- Existing dynamic/static gallery API import warning.
- Existing backend datetime deprecation warnings in gallery selection tests.

Sprint 8 status:

```text
Ready for release review.
```
