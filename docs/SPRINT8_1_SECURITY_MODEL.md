# Sprint 8.1 Security Model

Phase: 1 analysis only

No code changes were made.

## Security Goals

Sprint 8.1 hardens SaaS isolation and public media access without changing the
core domain workflows.

Goals:

- Authenticate users inside an explicit tenant context.
- Prevent Gallery UUIDs from acting as public secrets.
- Ensure expired Galleries cannot issue or use public access credentials.
- Remove known bootstrap passwords.
- Prevent deployment from silently resetting production passwords.
- Make shared audit logs tenant-queryable.
- Add regression tests for tenant and public access boundaries.

## Trust Boundaries

| Boundary | Trust Level | Rule |
| --- | --- | --- |
| Staff authenticated APIs | Trusted only after JWT and RBAC validation | Backend permissions and tenant scope are authoritative. |
| Public Gallery routes | Untrusted internet clients | Must use opaque access token and optional password session. |
| Public Delivery routes | Untrusted internet clients | Existing Delivery hardened token model remains reference. |
| Bootstrap scripts | Privileged operational code | Must fail closed in production without explicit secrets. |
| Audit logs | Security records | Must preserve tenant and branch context. |

## Tenant-Aware Login Model

### Required Login Factors

Login must require:

- `organization_code`
- `email`
- `password`

Authentication order:

1. Normalize organization code.
2. Load active organization by code.
3. Normalize email.
4. Load active user by `organization_id + email`.
5. Verify password using existing password hash behavior.
6. Issue access and refresh tokens.
7. Record tenant-scoped audit event.

### Duplicate Email Rule

The same email may exist in multiple organizations.

Correct behavior:

```text
organization_code = ALS + owner@example.com -> ALS owner
organization_code = DEMO + owner@example.com -> DEMO owner
```

Incorrect behavior:

```text
owner@example.com globally resolves to one arbitrary user
```

### JWT Claim Model

Access and refresh JWTs should include:

- `sub`: user id
- `type`: token type
- `jti`: token id
- `exp`: expiry
- `organization_id`: user's organization id
- `branch_id`: user's branch id, nullable

Authorization remains database-backed:

- `get_current_user()` should still load the user by `sub`.
- Tenant claims are context and defense-in-depth, not the only source of
  authorization.

### Rate Limiting

Rate-limit key should include:

- organization code
- email
- IP address

Recommended key:

```text
login:{organization_code}:{email}:{ip}
```

Production should require Redis-backed rate limiting.

## Gallery Public Access Security Model

### Current Risk

Gallery public URLs use Gallery UUIDs. A UUID is not a revocable access
credential and should not be the public secret for customer photos.

### Target Model

Introduce `GalleryAccessToken`.

Rules:

- Raw token is generated once and returned only at creation or rotation.
- Only `token_hash` is stored.
- Token is opaque and high entropy.
- Token belongs to exactly one Gallery.
- Token has an expiry timestamp.
- Token can be revoked.
- Token can be rotated.
- Public routes validate token before loading Gallery response data.
- Gallery UUID is never accepted as public access credential.

### Token Lifecycle

```text
Created -> Active -> Revoked
Created -> Active -> Expired
Active -> Rotated -> Revoked
```

Rotation behavior:

- Revoke existing active tokens for the Gallery.
- Create a new token hash.
- Return raw token once.
- Record audit event.

### Public Password Model

Gallery password remains optional.

If no password is configured:

- Valid `GalleryAccessToken` is enough.

If password is configured:

- Valid `GalleryAccessToken` is required.
- Correct password is required to issue a temporary gallery session token.
- Temporary session token should be short-lived.
- Session token must identify the Gallery and be bound to public access flow.

### Expiry Model

An expired Gallery must fail before:

- Password authentication.
- Public read.
- Public favorite creation.
- Public favorite deletion.
- Public selection submission.

Expired Gallery behavior:

```text
HTTP 410 Gone
```

### Public Route Model

Recommended target routes:

- `GET /api/v1/galleries/client/{token}`
- `POST /api/v1/galleries/client/{token}/authenticate`
- `POST /api/v1/galleries/client/{token}/favorites`
- `DELETE /api/v1/galleries/client/{token}/favorites/{favorite_id}`
- `POST /api/v1/galleries/client/{token}/submit-selection`

Staff management routes:

- `POST /api/v1/galleries/{gallery_id}/access-token/rotate`
- `POST /api/v1/galleries/{gallery_id}/access-token/revoke`

### Gallery Audit Events

Recommended audit events:

- `gallery.access_token_rotated`
- `gallery.access_token_revoked`
- `gallery.public_viewed`
- `gallery.password_authenticated`
- `gallery.favorite_selected`
- `gallery.favorite_removed`
- `gallery.selection_submitted`

Each event should include:

- `organization_id`
- `branch_id`
- `gallery_id`
- target id where applicable

## Bootstrap Security Model

### Current Risk

Bootstrap script contains known passwords and resets existing passwords during
idempotent execution.

### Target Rules

Production bootstrap must:

- Require `BOOTSTRAP_ADMIN_PASSWORD` or equivalent.
- Refuse known default passwords in production.
- Never reset existing passwords by default.
- Reset existing password only when an explicit force flag is set.
- Mark bootstrap-created users as requiring first-login password reset.

Recommended environment variables:

- `APP_ENV`
- `BOOTSTRAP_ADMIN_EMAIL`
- `BOOTSTRAP_ADMIN_USERNAME`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `BOOTSTRAP_FORCE_PASSWORD_RESET=false`
- `SEED_SAMPLE_TENANT=false`
- `SAMPLE_OWNER_PASSWORD`

Production behavior:

- If `APP_ENV=production` and required bootstrap secret is missing, fail.
- If user already exists and force flag is false, do not change password.
- If force flag is true, reset password and set `password_reset_required=true`.

Development behavior:

- May allow local defaults only when explicitly not production.
- Still should avoid resetting existing passwords by default.

## First-Login Password Reset Model

Add a user-level flag:

```text
password_reset_required
```

Initial Sprint 8.1 behavior:

- Login can succeed but response must tell frontend password reset is required,
  or login can return a controlled status requiring password reset.
- No broader password reset feature should be implemented unless approved.

Minimum safe behavior:

- Bootstrap-created users have `password_reset_required=true`.
- Auth response exposes the flag inside existing user payload if schema allows.
- Follow-up sprint can add a dedicated password reset screen if not included in
  Sprint 8.1 implementation approval.

## Tenant-Scoped Audit Model

### Required Columns

Add to `audit_logs`:

- `organization_id`
- `branch_id`

### Write Rules

Audit writer should accept:

- explicit `organization_id`
- explicit `branch_id`

Fallback inference:

- If actor user exists, infer from actor.
- If metadata contains valid organization or branch id, use metadata.
- If no scope is known, allow null only for platform/system events.

### Query Rules

Future audit list/export APIs must filter by:

- `organization_id` for tenant admins
- `branch_id` for branch-scoped users

Platform admins may query globally.

## Security Regression Suite

Backend test categories:

- Tenant-aware login.
- Duplicate email across organizations.
- JWT tenant and branch claims.
- Refresh token compatibility.
- Gallery access token lifecycle.
- Gallery expired behavior.
- Bootstrap production fail-closed behavior.
- Bootstrap non-reset behavior.
- Audit tenant and branch writes.
- Cross-tenant access denial.

Frontend test categories:

- Login requires organization code.
- Login submits organization code.
- Public Gallery uses token routes.
- Public Gallery password flow still works.
- Expired/revoked Gallery token error state.
- Staff token rotate/revoke controls.

## Security Non-Goals

Sprint 8.1 should not add:

- Public self-signup.
- Billing or subscriptions.
- Separate tenant databases.
- Separate tenant schemas.
- New booking, editing, or delivery workflow features.
- A full password recovery system unless separately approved.

## Security Approval Criteria

Sprint 8.1 should not be considered complete until:

- Email-only login no longer works.
- Duplicate emails across organizations are tested.
- Gallery UUID no longer retrieves public Gallery data.
- Gallery token revocation, expiry, and rotation are tested.
- Expired Gallery cannot authenticate or submit selections.
- Bootstrap does not reset existing passwords without explicit force flag.
- Shared audit rows include tenant scope for new business events.
- Full backend and frontend validation passes.
