# Sprint 8.1 Implementation Plan

Phase: 1 analysis only

No code changes were made. Implementation must wait for approval.

## Objective

Sprint 8.1 hardens ALRSCRM for multi-tenant SaaS use by addressing:

1. Tenant-aware login.
2. Gallery public access tokens.
3. Gallery expiry authentication bug.
4. Bootstrap password hardening.
5. Tenant-scoped audit logs.
6. Security regression test coverage.

## Execution Guardrail

Do not start Phase 2 implementation until Phase 1 documents are reviewed and
approved.

Phase 1 deliverables:

- `docs/SPRINT8_1_ARCHITECTURE_REVIEW.md`
- `docs/SPRINT8_1_SECURITY_MODEL.md`
- `docs/SPRINT8_1_IMPLEMENTATION_PLAN.md`

`docs/SPRINT8_1_COMPLETION_REPORT.md` should be created only after
implementation and verification are complete.

## Phase 2 Backend Implementation Plan

### 1. Tenant-Aware Login

Backend changes:

- Update `LoginRequest` to require `organization_code`.
- Add organization lookup by normalized code.
- Add user lookup by `organization_id + email`.
- Update `authenticate_user()` signature.
- Update auth route call site.
- Keep password verification unchanged.
- Keep RBAC unchanged.
- Update login audit metadata to include organization code and tenant scope.
- Update rate-limit key to include organization code.

Files:

- `backend/app/auth/schemas.py`
- `backend/app/auth/routes.py`
- `backend/app/auth/service.py`
- `backend/app/auth/rate_limit.py`
- `backend/app/identity/services/user_service.py`
- `backend/app/identity/services/organization_service.py`

Tests:

- Duplicate email across organizations.
- Correct organization login succeeds.
- Wrong organization login fails.
- Old email-only payload fails validation.

### 2. JWT Tenant Claims

Backend changes:

- Add optional claims support to token creation.
- Issue access and refresh tokens with:
  - `organization_id`
  - `branch_id`
- Keep `sub` as user id.
- Keep `get_current_user()` database-backed.
- Ensure refresh token rotation still works.

Files:

- `backend/app/core/security.py`
- `backend/app/auth/service.py`
- `backend/app/api/deps.py`

Tests:

- Decode issued access token and assert tenant claims.
- Refresh token call succeeds and issues tenant claims.

### 3. Tenant-Scoped Audit Logs

Migration:

- Add `organization_id` and `branch_id` to `audit_logs`.
- Add indexes for tenant-safe queries.
- Backfill from `users` where `actor_user_id` exists.
- Backfill from `metadata_json` where present and valid.

Backend changes:

- Extend `record_audit_event()` parameters:
  - `organization_id`
  - `branch_id`
- Infer scope from actor user when explicit scope is absent.
- Update high-value service calls to pass explicit scope, especially public
  Gallery and Delivery flows.

Files:

- `backend/app/shared/models/audit_log.py`
- `backend/app/shared/services/audit_service.py`
- services that call `record_audit_event`
- new Alembic migration

Tests:

- New audit rows include organization and branch.
- Public Gallery audit writes include scope.
- Platform/system audit can remain nullable only when no tenant exists.

### 4. Bootstrap Hardening

Backend changes:

- Replace hardcoded passwords with environment-driven values.
- Refuse missing admin password in production.
- Refuse known default passwords in production.
- Do not reset existing user password by default.
- Add explicit force-reset environment flag.
- Add `password_reset_required` support.

Migration:

- Add `users.password_reset_required`.

Files:

- `backend/scripts/seed_super_admin.py`
- `backend/app/identity/models/user.py`
- `backend/app/identity/schemas/user.py`
- new Alembic migration
- `backend/.env.example`
- Docker docs if needed

Tests:

- Script creates bootstrap user with env password.
- Script does not reset existing password by default.
- Force reset changes password only when explicit flag is set.
- Production mode without password fails.
- Bootstrap-created user has `password_reset_required=true`.

### 5. Gallery Access Token Model

Migration:

- Add `gallery_access_tokens`.

Model:

- `GalleryAccessToken`
  - `id`
  - `gallery_id`
  - `token_hash`
  - `expires_at`
  - `created_at`
  - `last_accessed_at`
  - `revoked_at`
  - `created_by_user_id`

Backend changes:

- Add repository methods:
  - create token
  - active token lookup by hash
  - active tokens by Gallery
  - revoke active tokens
- Add service methods:
  - validate public token
  - rotate token
  - revoke token
  - central public expiry guard
- Replace public UUID routes with token routes.
- Update public favorite and submit workflows to resolve Gallery from token.
- Ensure Gallery UUID no longer returns public data.

Files:

- `backend/app/galleries/models/gallery.py`
- `backend/app/galleries/repositories.py`
- `backend/app/galleries/schemas/gallery.py`
- `backend/app/galleries/services/gallery_service.py`
- `backend/app/galleries/routes.py`
- new Alembic migration

Tests:

- Token can view Gallery.
- UUID route no longer exposes Gallery.
- Revoked token fails.
- Expired token fails.
- Rotated token invalidates old token.
- Expired Gallery cannot authenticate.
- Expired Gallery cannot submit selection.

### 6. Backend Verification

Run after backend implementation:

```bash
ruff check backend frontend
ruff format --check backend frontend
python -m pytest backend/tests
cd backend
alembic upgrade head
```

If Docker database is required:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

## Phase 3 Frontend Implementation Plan

### 1. Tenant-Aware Login UI

Frontend changes:

- Add Organization Code field to login page.
- Update login types and API request.
- Update auth context payload.
- Update tests.
- Regenerate OpenAPI types after backend starts.

Files:

- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/LoginPage.test.tsx`
- `frontend/src/types/auth.ts`
- `frontend/src/api/auth.ts`
- `frontend/src/contexts/AuthContext.tsx`
- generated OpenAPI files

### 2. Public Gallery Token UI

Frontend changes:

- Change client gallery route from Gallery UUID to token.
- Update public Gallery API adapter.
- Update public password authentication call.
- Store session access by token route key, not Gallery UUID.
- Update tests.

Files:

- `frontend/src/routes/AppRoutes.tsx`
- `frontend/src/api/galleries.ts`
- `frontend/src/types/galleries.ts`
- `frontend/src/modules/bookings/ClientSelectionPage.tsx`
- `frontend/src/modules/bookings/ClientSelectionPage.test.tsx`

### 3. Staff Gallery Token Controls

Frontend changes:

- Add rotate token action.
- Add revoke token action.
- Add copy client link action after rotation response.
- Keep behavior visible only to staff users who can manage Gallery.

Files:

- `frontend/src/modules/bookings/GalleryDetailsPage.tsx`
- `frontend/src/modules/bookings/GalleryDetailsPage.test.tsx`

### 4. Frontend Verification

Run:

```bash
cd frontend
npm run lint
npm run test
npm run build
npm run generate:api-types
```

## Phase 4 Full Repository Verification

Required commands:

```bash
python -m pytest backend/tests
cd frontend
npm run lint
npm run test
npm run build
npm run generate:api-types
cd ..
docker compose up -d --build
docker compose exec api alembic upgrade head
```

Also run:

```bash
ruff check backend frontend
ruff format --check backend frontend
```

## Rollback Strategy

### Pre-Deployment

- Take a database backup.
- Record existing public Gallery links that will be invalidated.
- Communicate that new tokenized Gallery links must be issued.

### Schema Rollback

Downgrade migration must:

- Drop `gallery_access_tokens`.
- Drop Sprint 8.1 audit indexes.
- Drop `audit_logs.organization_id`.
- Drop `audit_logs.branch_id`.
- Drop `users.password_reset_required`.

### Application Rollback

- Roll back backend and frontend together.
- Do not run old frontend against new token-only Gallery APIs.
- Do not run new frontend against old UUID Gallery APIs.

### Operational Risks

- Tokenized Gallery links created during Sprint 8.1 stop working after rollback.
- Audit rows written with new tenant columns lose query efficiency if rolled
  back.
- If tenant-aware login is rolled back, duplicate-email tenants remain
  ambiguous.

## Release Acceptance Criteria

Sprint 8.1 can be marked complete only when:

- `organization_code` is required at login.
- Duplicate email across organizations is supported and tested.
- JWT contains organization and branch claims.
- Refresh token rotation still passes.
- Gallery UUID no longer functions as public secret.
- Gallery access tokens support expiry, revocation, and rotation.
- Expired Gallery cannot authenticate or submit selections.
- Bootstrap has no hardcoded production passwords.
- Existing bootstrap user passwords are not reset silently.
- Shared audit logs store tenant and branch scope for new writes.
- Full backend and frontend verification passes.
- `docs/SPRINT8_1_COMPLETION_REPORT.md` is created with results.

## Estimated Effort

| Workstream | Estimate |
| --- | --- |
| Tenant-aware login backend | 0.5-1 day |
| JWT claims and refresh compatibility | 0.5 day |
| Audit log migration and service updates | 1 day |
| Bootstrap hardening and tests | 0.5-1 day |
| Gallery access token backend | 1.5-2 days |
| Frontend login and Gallery token migration | 1-1.5 days |
| Regression tests and OpenAPI generation | 1 day |
| Docker and release validation | 0.5 day |

Recommended sprint size:

```text
5-7 engineering days
```

## Phase 1 Status

Phase 1 analysis is complete after creation of:

- `docs/SPRINT8_1_ARCHITECTURE_REVIEW.md`
- `docs/SPRINT8_1_SECURITY_MODEL.md`
- `docs/SPRINT8_1_IMPLEMENTATION_PLAN.md`

Implementation is intentionally not started.
