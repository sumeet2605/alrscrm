# Sprint 8.1 Completion Report

Sprint 8.1 implements SaaS Security Hardening.

## Completed Scope

Completed:

- Tenant-aware login using `organization_code + email + password`
- Organization-scoped user lookup for authentication
- JWT tenant and branch claims
- Refresh token compatibility with tenant claims
- Login rate-limit key scoped by organization code
- Gallery public access token model
- Tokenized public Gallery client routes
- Gallery access token rotation
- Gallery access token revocation
- Gallery token expiry validation
- Gallery expiry authentication bug fix
- Bootstrap password hardening
- First-login password reset marker on users
- Tenant and branch scoped shared audit logs
- Backend security regression tests
- Frontend tenant-aware login changes
- Frontend token-based client Gallery route
- Staff Gallery rotate/revoke/copy link workflow
- OpenAPI TypeScript type regeneration

## Backend Files Created

- `backend/alembic/versions/202606100016_saas_security_hardening.py`

## Backend Files Updated

- `backend/.env.example`
- `backend/app/auth/rate_limit.py`
- `backend/app/auth/routes.py`
- `backend/app/auth/schemas.py`
- `backend/app/auth/service.py`
- `backend/app/core/security.py`
- `backend/app/galleries/models/__init__.py`
- `backend/app/galleries/models/gallery.py`
- `backend/app/galleries/repositories.py`
- `backend/app/galleries/routes.py`
- `backend/app/galleries/schemas/__init__.py`
- `backend/app/galleries/schemas/gallery.py`
- `backend/app/galleries/services/gallery_service.py`
- `backend/app/identity/models/user.py`
- `backend/app/identity/schemas/user.py`
- `backend/app/identity/services/user_service.py`
- `backend/app/shared/models/audit_log.py`
- `backend/app/shared/services/audit_service.py`
- `backend/scripts/seed_super_admin.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_delivery_api.py`
- `backend/tests/test_editing_api.py`
- `backend/tests/test_galleries_api.py`
- `backend/tests/test_galleries_selection.py`
- `backend/tests/test_seed_super_admin.py`

## Frontend Files Updated

- `frontend/src/api/galleries.ts`
- `frontend/src/modules/bookings/ClientSelectionPage.tsx`
- `frontend/src/modules/bookings/ClientSelectionPage.test.tsx`
- `frontend/src/modules/bookings/GalleryDetailsPage.tsx`
- `frontend/src/modules/bookings/GalleryDetailsPage.test.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/LoginPage.test.tsx`
- `frontend/src/routes/AppRoutes.tsx`
- `frontend/src/types/auth.ts`
- `frontend/src/types/galleries.ts`
- `frontend/src/types/generated/openapi-schema.json`
- `frontend/src/types/generated/openapi.ts`

## Documentation Created

- `docs/SPRINT8_1_ARCHITECTURE_REVIEW.md`
- `docs/SPRINT8_1_SECURITY_MODEL.md`
- `docs/SPRINT8_1_IMPLEMENTATION_PLAN.md`
- `docs/SPRINT8_1_COMPLETION_REPORT.md`

## Migration

Created migration:

- `202606100016_saas_security_hardening`

Migration changes:

- Adds `users.password_reset_required`
- Adds `audit_logs.organization_id`
- Adds `audit_logs.branch_id`
- Adds audit tenant and branch indexes
- Backfills audit tenant and branch scope from actor users and metadata
- Creates `gallery_access_tokens`

Rollback drops:

- `gallery_access_tokens`
- Sprint 8.1 audit indexes
- `audit_logs.organization_id`
- `audit_logs.branch_id`
- `users.password_reset_required`

## API Changes

### Authentication

`POST /api/v1/auth/login` now requires:

```json
{
  "organization_code": "ALRSCRM",
  "email": "admin@admin.com",
  "password": "..."
}
```

JWT access and refresh tokens now include:

- `organization_id`
- `branch_id`

### Gallery Public Access

New token-based public routes:

- `GET /api/v1/galleries/client/{access_token}`
- `POST /api/v1/galleries/client/{access_token}/authenticate`
- `POST /api/v1/galleries/client/{access_token}/favorites`
- `DELETE /api/v1/galleries/client/{access_token}/favorites/{favorite_id}`
- `POST /api/v1/galleries/client/{access_token}/submit-selection`

New staff routes:

- `POST /api/v1/galleries/{gallery_id}/access-token/rotate`
- `POST /api/v1/galleries/{gallery_id}/access-token/revoke`

Old UUID public Gallery routes no longer return public Gallery data because the
service treats the route value as an access token.

## Security Improvements

- Duplicate emails across organizations are supported during login.
- Login is tenant-scoped by organization code.
- Gallery UUID no longer functions as the public secret.
- Gallery access tokens are opaque and stored as hashes.
- Gallery tokens support expiry, revocation, and rotation.
- Expired Galleries cannot authenticate or submit selections.
- Bootstrap script no longer contains hardcoded passwords.
- Existing bootstrap users are not silently reset.
- Force password reset requires explicit environment flag.
- Shared audit log rows can store tenant and branch scope.

## Bootstrap Notes

New environment variables:

- `BOOTSTRAP_ADMIN_EMAIL`
- `BOOTSTRAP_ADMIN_USERNAME`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `BOOTSTRAP_FORCE_PASSWORD_RESET`
- `SAMPLE_OWNER_PASSWORD`
- `SAMPLE_OWNER_FORCE_PASSWORD_RESET`

Important behavior:

- Creating a new bootstrap admin requires `BOOTSTRAP_ADMIN_PASSWORD`.
- Existing bootstrap user passwords are preserved by default.
- Password reset only happens when `BOOTSTRAP_FORCE_PASSWORD_RESET=true`.
- Production rejects missing, weak, or known default bootstrap passwords.

## Verification

Completed:

```text
ruff check backend frontend: passed
ruff format --check backend frontend: passed
python -m pytest backend/tests: passed, 59 tests
npm run lint: passed
npm run test: passed, 32 tests
npm run build: passed
npm run generate:api-types: passed
docker compose up -d --build: passed
docker compose exec api alembic upgrade head: passed
```

Non-blocking warnings observed:

- Existing frontend Ant Design `act(...)` warning in `DashboardLayout.test.tsx`.
- Existing frontend dynamic/static import warning for `frontend/src/api/galleries.ts`.
- Existing frontend bundle size warning.
- Existing backend datetime deprecation warnings in Gallery selection tests.

## Regression Coverage Added Or Updated

Backend:

- Organization code required during login.
- Duplicate email login is scoped by organization.
- Wrong tenant password combination fails.
- JWT includes tenant claims.
- Public Gallery access uses token routes.
- UUID public Gallery route no longer exposes data.
- Gallery token rotation works.
- Gallery token revocation path is covered.
- Expired Gallery cannot authenticate or submit selection.
- Bootstrap requires env password for new user creation.
- Bootstrap does not reset existing password by default.
- Bootstrap force reset only works with explicit flag.

Frontend:

- Login form submits organization code.
- Client Gallery route uses public token.
- Staff Gallery share flow rotates tokenized links.

## Rollout Notes

- Existing UUID Gallery public links should be reissued through the new Rotate
  Link action.
- Fresh Docker/bootstrap environments must provide `BOOTSTRAP_ADMIN_PASSWORD`
  before first bootstrap user creation.
- Existing Docker volumes with an existing bootstrap admin continue without
  password reset.

## Sprint 8.1 Status

Sprint 8.1 is implemented and verified.

Recommended next sprint:

- Add a dedicated first-login password reset screen and invite-token workflow.
- Add tenant-scoped audit listing/export APIs.
- Harden production rate limiting to require Redis in non-local environments.
