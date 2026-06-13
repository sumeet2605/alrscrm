# Sprint 8.1 Architecture Review

Phase: 1 analysis only

Reviewed branch: `development`

No backend, frontend, migration, or test implementation changes were made.

## Review Scope

Sprint 8.1 hardens the SaaS security boundaries introduced through Sprint 8.
The current architecture is:

- Shared database
- Shared schema
- Multi-organization
- `organization_id` is the tenant boundary
- `branch_id` is the operational branch boundary

Reviewed areas:

- Authentication and JWT issuance
- Identity and user lookup
- Organization onboarding and bootstrap
- Gallery public access
- Delivery public access as a reference model
- Shared audit logging
- Frontend login and public client gallery flow
- Existing tests and migration patterns

## Current Architecture Findings

### Tenant-Aware Login Gap

Current login accepts only:

- `email`
- `password`

Evidence:

- `backend/app/auth/schemas.py`
- `backend/app/auth/routes.py`
- `backend/app/auth/service.py`
- `backend/app/identity/services/user_service.py`
- `frontend/src/pages/LoginPage.tsx`

`authenticate_user()` calls `get_user_by_email(db, email)`. The user lookup is
not scoped by organization. This is incompatible with SaaS behavior where
`owner@example.com` can exist in multiple organizations.

Required architecture change:

- Login request must include `organization_code`.
- Backend must resolve the organization first.
- User lookup must become `organization_id + email`.
- Existing password hashing and validation should stay unchanged.
- RBAC should continue to derive from the loaded user and roles.

### JWT Claims Gap

Current access and refresh tokens carry:

- `sub`
- `type`
- `jti`
- `exp`

They do not carry:

- `organization_id`
- `branch_id`

Current route authorization still works because `get_current_user()` loads the
user from the database. Sprint 8.1 should add tenant and branch claims for
traceability and future gateway/security use, while keeping database-backed
authorization authoritative.

Required architecture change:

- Add optional custom claims support to token creation.
- Issue access and refresh tokens with `organization_id` and `branch_id`.
- Keep refresh token rotation compatible with existing sessions.
- Continue loading current user from the database.

### Gallery Public Access Gap

Current public Gallery APIs are UUID-based:

- `GET /api/v1/galleries/{gallery_id}/public`
- `POST /api/v1/galleries/{gallery_id}/public/favorites`
- `DELETE /api/v1/galleries/{gallery_id}/public/favorites/{favorite_id}`
- `POST /api/v1/galleries/public/{gallery_id}/authenticate`
- `POST /api/v1/galleries/{gallery_id}/public/submit-selection`

Evidence:

- `backend/app/galleries/routes.py`
- `backend/app/galleries/services/gallery_service.py`
- `frontend/src/modules/bookings/ClientSelectionPage.tsx`

The Gallery UUID currently acts as the public secret when no password is set.
This is weaker than the hardened Delivery model introduced in Sprint 7.1.

Required architecture change:

- Introduce `GalleryAccessToken` as Gallery-owned public access credential.
- Public routes should use opaque tokens, not Gallery UUIDs.
- Store only token hashes.
- Support token expiry, revocation, and rotation.
- Preserve Gallery as the selection aggregate root.

### Gallery Expiry Bug

`authenticate_public_gallery()` has an unreachable expiry validation block
nested under a `raise NotFoundError`. Expired password-protected galleries can
issue an authentication token even though later public reads reject expired
galleries.

Required architecture change:

- Centralize public Gallery expiry validation.
- Apply it consistently before authenticate, read, favorite mutation, and
  selection submission.

### Bootstrap Architecture Gap

`backend/scripts/seed_super_admin.py` currently contains static credentials and
updates existing user passwords during idempotent runs.

Evidence:

- `ADMIN_PASSWORD = "Admin@123"`
- `SAMPLE_OWNER_PASSWORD = "Owner@123"`
- Existing users are assigned a new `password_hash` in `_ensure_user()`.
- `docker-compose.prod.yml` runs `python -m scripts.seed_super_admin`.

Required architecture change:

- Bootstrap credentials must come from environment variables.
- Existing passwords must never reset silently.
- A force-reset flag must be explicit.
- First-login password reset support requires a user state column or equivalent
  migration-safe marker.

### Audit Scope Gap

`AuditLog` currently stores:

- `actor_user_id`
- `action`
- `target_type`
- `target_id`
- `metadata_json`
- `created_at`

It does not store first-class:

- `organization_id`
- `branch_id`

Required architecture change:

- Add nullable tenant and branch columns to `audit_logs`.
- Backfill existing rows where possible.
- Update audit writer to accept scope explicitly or infer from actor.
- Add indexes for tenant-safe query patterns.

## Gap Analysis

| Gap | Severity | Current Risk | Required Direction |
| --- | --- | --- | --- |
| Email-only login | Critical | Duplicate tenant emails cannot authenticate safely. | `organization_code + email + password`. |
| JWT lacks tenant claims | Major | Tokens cannot be audited or inspected with tenant context. | Add `organization_id` and `branch_id` claims. |
| UUID public Gallery links | Critical | Gallery UUID acts as public secret. | Opaque hashed access tokens. |
| Gallery expiry auth bug | Major | Expired galleries can issue auth token. | Central expiry guard. |
| Static bootstrap passwords | Critical | Known credentials can exist in production. | Env-only bootstrap secrets. |
| Silent password reset during bootstrap | Critical | Deployment can reset admin password. | Never reset unless explicit flag. |
| Audit logs not tenant-scoped | Major | Tenant-safe audit export is weak. | Columns, backfill, indexes. |
| Frontend login lacks org code | Critical | Cannot use tenant-aware backend login. | Add organization code field. |
| Client Gallery route stores access by gallery UUID | Major | Old route model persists in UX. | Token route and token-scoped storage. |

## Impacted Files

### Backend Auth

- `backend/app/auth/schemas.py`
- `backend/app/auth/routes.py`
- `backend/app/auth/service.py`
- `backend/app/auth/rate_limit.py`
- `backend/app/core/security.py`
- `backend/app/api/deps.py`
- `backend/app/identity/services/user_service.py`
- `backend/app/identity/services/organization_service.py`

### Backend Gallery

- `backend/app/galleries/models/gallery.py`
- `backend/app/galleries/models/__init__.py`
- `backend/app/galleries/repositories.py`
- `backend/app/galleries/schemas/gallery.py`
- `backend/app/galleries/schemas/__init__.py`
- `backend/app/galleries/services/gallery_service.py`
- `backend/app/galleries/routes.py`

### Backend Audit And Bootstrap

- `backend/app/shared/models/audit_log.py`
- `backend/app/shared/services/audit_service.py`
- `backend/app/shared/models/__init__.py`
- `backend/scripts/seed_super_admin.py`
- `backend/app/identity/models/user.py`
- `backend/app/identity/schemas/user.py`
- `backend/alembic/env.py`
- new Alembic migration

### Frontend

- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/LoginPage.test.tsx`
- `frontend/src/types/auth.ts`
- `frontend/src/api/auth.ts`
- `frontend/src/contexts/AuthContext.tsx`
- `frontend/src/api/galleries.ts`
- `frontend/src/types/galleries.ts`
- `frontend/src/modules/bookings/ClientSelectionPage.tsx`
- `frontend/src/modules/bookings/ClientSelectionPage.test.tsx`
- `frontend/src/modules/bookings/GalleryDetailsPage.tsx`

### Tests

- `backend/tests/test_auth.py`
- `backend/tests/test_identity_api.py`
- `backend/tests/test_galleries_api.py`
- `backend/tests/test_galleries_selection.py`
- `backend/tests/test_seed_super_admin.py`
- frontend login and client gallery tests

## Migration Impact Review

Sprint 8.1 needs one migration with three independent areas:

1. Add `gallery_access_tokens`.
2. Add tenant columns and indexes to `audit_logs`.
3. Add first-login password reset marker to users.

Recommended migration entities:

### `gallery_access_tokens`

Columns:

- `id`
- `gallery_id`
- `token_hash`
- `expires_at`
- `created_at`
- `last_accessed_at`
- `revoked_at`
- `created_by_user_id`

Constraints and indexes:

- FK `gallery_id -> galleries.id`
- FK `created_by_user_id -> users.id`
- unique `token_hash`
- index `gallery_id`
- index `expires_at`
- partial or normal index for `revoked_at`

No raw token should be persisted.

### `audit_logs`

Add nullable:

- `organization_id`
- `branch_id`

Indexes:

- `ix_audit_logs_organization_created_at`
- `ix_audit_logs_branch_created_at`
- optional `ix_audit_logs_organization_action_created_at`

Backfill:

- If `actor_user_id` is present, use `users.organization_id` and
  `users.branch_id`.
- If metadata has `organization_id` or `branch_id`, use metadata for rows
  without actor.
- Rows that cannot be inferred remain null.

### `users`

Add:

- `password_reset_required boolean not null default false`

This supports bootstrap-created users without changing auth contracts beyond
the login response behavior.

## API Impact Review

### Login API

Current:

```text
POST /api/v1/auth/login
{
  "email": "...",
  "password": "..."
}
```

Target:

```text
POST /api/v1/auth/login
{
  "organization_code": "ALS",
  "email": "...",
  "password": "..."
}
```

Compatibility option:

- Make `organization_code` required for production behavior.
- Tests and seed users must be updated.
- OpenAPI types must be regenerated after implementation.

### Token Response

Response shape should remain backward compatible:

- `access_token`
- `refresh_token`
- `token_type`
- `user`

JWT internals may add:

- `organization_id`
- `branch_id`

### Gallery Public APIs

Target public route shape:

- `GET /api/v1/galleries/client/{token}`
- `POST /api/v1/galleries/client/{token}/authenticate`
- `POST /api/v1/galleries/client/{token}/favorites`
- `DELETE /api/v1/galleries/client/{token}/favorites/{favorite_id}`
- `POST /api/v1/galleries/client/{token}/submit-selection`

Staff route additions:

- `POST /api/v1/galleries/{gallery_id}/access-token/rotate`
- `POST /api/v1/galleries/{gallery_id}/access-token/revoke`

Backward compatibility:

- Staff APIs stay unchanged.
- Old UUID public routes should be removed or return a controlled failure after
  frontend migration.
- If a temporary compatibility window is needed, old routes must not disclose
  gallery data and should only return a deprecation response.

## Frontend Impact Review

### Login Page

Add `Organization Code` field before email.

Validation:

- Required.
- Uppercase normalization can happen client-side for UX, but backend remains
  authoritative.

Storage:

- Existing access and refresh token storage remains unchanged.
- Optionally remember last organization code in local storage for UX.

### Client Gallery Page

Current route parameter is `galleryId`.

Target route parameter should be access token:

- `/client/gallery/:token`

Client storage:

- Do not key public gallery session by Gallery UUID.
- Store password-auth session token by access token hash surrogate or route
  token key.

### Gallery Details Page

Staff should be able to:

- Rotate public Gallery token.
- Revoke public Gallery token.
- Copy new public client link.

This can be minimal in Sprint 8.1 but must not expose raw tokens after the
initial rotate/create response.

## Test Impact Review

Required backend tests:

- Login succeeds with `organization_code + email + password`.
- Same email in two organizations logs into the requested tenant.
- Wrong organization code fails.
- Refresh token flow still works after tenant claims are added.
- Access token contains organization and branch claims.
- Cross-tenant access remains denied after login changes.
- Gallery access token can retrieve public Gallery.
- Gallery UUID cannot retrieve public Gallery.
- Gallery revoked token fails.
- Gallery expired token fails.
- Rotating Gallery token invalidates the old token.
- Expired Gallery cannot authenticate.
- Expired Gallery cannot submit selection.
- Audit rows include `organization_id` and `branch_id` for new writes.
- Audit backfill migration handles actor-scoped rows.
- Bootstrap fails in production mode without required passwords.
- Bootstrap does not reset existing password by default.
- Bootstrap force reset works only when explicit flag is set.
- Bootstrap-created users require first password reset.

Required frontend tests:

- Login requires organization code.
- Login submits organization code to API.
- Login failure renders error state.
- Client Gallery uses token route.
- Password-protected Gallery authenticates using token route.
- Revoked or expired token shows access error.
- Gallery details exposes rotate/revoke/copy controls for authorized staff.

## Rollback Strategy

### Code Rollback

- Revert Sprint 8.1 code changes and OpenAPI generated types together.
- Keep migration rollback tested separately.

### Migration Rollback

Rollback must:

- Drop `gallery_access_tokens`.
- Drop audit indexes added in Sprint 8.1.
- Drop `audit_logs.organization_id`.
- Drop `audit_logs.branch_id`.
- Drop `users.password_reset_required`.

Risk:

- Any Gallery public links created during Sprint 8.1 become invalid after
  rollback.
- If old UUID public routes are removed, rollback restores old behavior only if
  code is rolled back with schema rollback.

### Operational Rollback

- Communicate that Gallery share links issued during Sprint 8.1 may need to be
  reissued.
- Do not rollback after tenants have been told UUID links are invalid unless
  client communication is handled.
- Keep a database backup before migration.

## Architecture Recommendation

Proceed with Sprint 8.1 after approval.

Implementation should prioritize backend security boundaries first:

1. Tenant-aware login.
2. Bootstrap hardening.
3. Tenant-scoped audit logs.
4. Gallery access tokens.
5. Frontend migration.
6. Full regression suite.

Do not introduce unrelated business features in Sprint 8.1.
