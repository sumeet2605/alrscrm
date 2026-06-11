# Default Organization Implementation Plan

Target default organization:

```text
Organization Name: Alluring Lens Studios
Default Branch: Main Studio
Owner: System-created during bootstrap
```

This is a plan only. No code changes were made as part of this review.

## Current State

### Development Bootstrap

`backend/scripts/seed_super_admin.py` currently creates:

- Organization code: `ALRS`
- Organization name: `ALRSCRM`
- Super Admin username: `admin`
- Super Admin email: `admin@admin.com`
- Super Admin password: `Admin@123`

It does not create:

- Default branch
- Owner user
- Organization setup state

### Production Bootstrap

`docker-compose.prod.yml` currently runs:

- Alembic migrations
- Identity seed
- Sales seed

It does not run:

- Super Admin seed
- Default organization seed
- Default branch seed

### Startup Validation

Application startup validates identity seed data, but it does not validate that
a default organization or branch exists.

## Required Behavior

The bootstrap process should be idempotent and should ensure:

1. `Alluring Lens Studios` organization exists.
2. `Main Studio` branch exists under that organization.
3. Super Admin is linked to the organization.
4. A system-created Owner exists or is prepared for that organization.
5. Existing migrations continue to work.
6. Existing tests continue to pass.
7. Tenant and branch isolation rules remain unchanged.

## Recommended Design

### Bootstrap Mechanism

Use an idempotent bootstrap service or script, not an Alembic data migration.

Reasoning:

- Alembic should remain focused on schema.
- Environment-specific credentials should not live in migrations.
- Bootstrap can be safely re-run in Docker, local development, staging, and
  production.

Recommended script:

```text
backend/scripts/bootstrap_default_organization.py
```

The script should be called after:

```text
alembic upgrade head
python -m scripts.seed_identity
python -m scripts.seed_sales
```

### Organization Identity

Recommended organization code:

```text
ALRS
```

Reasoning:

- The current super admin seed already uses `ALRS`.
- Reusing the code avoids breaking existing development data.
- Existing `ALRSCRM` rows can be updated in place to the new display name.

Bootstrap rule:

1. Find organization by code `ALRS`.
2. If found, update its name to `Alluring Lens Studios` and keep the same ID.
3. If not found, create it with code `ALRS` and name
   `Alluring Lens Studios`.

### Default Branch

Recommended default branch:

```text
Name: Main Studio
Code: MAIN
```

Bootstrap rule:

1. Find branch by `(organization_id, code = MAIN)`.
2. If found, update name and active state if needed.
3. If not found, create it.

This preserves the current unique branch constraint:

```text
(organization_id, code)
```

### Super Admin Link

Keep the existing Super Admin account behavior:

```text
username: admin
email: admin@admin.com
```

Bootstrap rule:

1. Ensure Super Admin role exists.
2. Find the Super Admin user by email.
3. If missing, create the user.
4. Link user to `Alluring Lens Studios`.
5. Keep `branch_id` nullable for platform-level Super Admin unless a product
   decision requires default branch assignment.
6. Ensure the user has the `Super Admin` role.

### Owner User

The requirement says Owner is system-created during bootstrap. This should be
done without hardcoding production credentials.

Recommended environment variables:

```text
DEFAULT_OWNER_EMAIL
DEFAULT_OWNER_USERNAME
DEFAULT_OWNER_PASSWORD
DEFAULT_OWNER_FIRST_NAME
DEFAULT_OWNER_LAST_NAME
```

Recommended behavior:

1. If owner email and password are configured, create or update an active Owner.
2. Assign the Owner role.
3. Link Owner to `Alluring Lens Studios`.
4. Link Owner to `Main Studio`.
5. If owner credentials are not configured in production, either:
   - skip Owner creation and fail startup with a clear error, or
   - create an inactive Owner and require an invite/password setup flow.

Preferred production behavior:

```text
Fail closed when required owner bootstrap credentials are missing.
```

### Idempotency Rules

The bootstrap should be safe to run repeatedly.

Required idempotency checks:

- Organization lookup by code.
- Branch lookup by organization and code.
- Super Admin lookup by email.
- Owner lookup by organization and email.
- Role assignment should append only if missing.
- Existing IDs should be preserved.
- Password reset behavior should be explicit and environment-controlled.

### Multi-Tenant Safety

The bootstrap must not weaken multi-tenant isolation.

Rules:

- Do not remove organization or branch filters from services.
- Do not create global business records without `organization_id`.
- Do not assign non-platform users to another tenant.
- Do not make `branch_id` optional for branch-owned business records.
- Do not use bootstrap data as a fallback tenant for runtime APIs.

## Migration Strategy

No schema migration is required for the default organization itself.

Possible migration only if later needed:

- Add organization settings table.
- Add onboarding status table.
- Add first-class audit log tenant columns.

The default organization creation should remain seed/bootstrap data, not schema
data.

## Test Plan

Backend tests:

- Bootstrap creates `Alluring Lens Studios` when no organization exists.
- Bootstrap renames existing `ALRSCRM` organization with code `ALRS`.
- Bootstrap creates `Main Studio`.
- Bootstrap is idempotent across multiple runs.
- Super Admin is linked to the default organization.
- Owner is linked to the default organization and default branch.
- Existing identity tests continue to pass.
- Existing tenant isolation tests continue to pass.

Frontend tests:

- No frontend changes are required for the default bootstrap sprint.
- Future onboarding sprint should add organization UI tests.

Docker tests:

- Dev Docker runs bootstrap successfully.
- Production Docker has a documented bootstrap path.
- `alembic upgrade head` remains independent from bootstrap data.

## Rollout Plan

1. Add idempotent bootstrap script/service.
2. Update dev Docker startup to call it.
3. Decide whether production Docker should call it automatically or require a
   one-time operational command.
4. Add environment variables to `.env.example`.
5. Add tests for idempotency and existing-data compatibility.
6. Document local, staging, and production bootstrap commands.

## Backward Compatibility

Backward-compatible choices:

- Preserve organization code `ALRS`.
- Update display name from `ALRSCRM` to `Alluring Lens Studios`.
- Preserve existing Super Admin email and username.
- Add `Main Studio` branch without changing existing branch data.
- Do not change API contracts.
- Do not change existing migration semantics.

## Risks

| Risk | Mitigation |
| --- | --- |
| Existing installs already have `ALRSCRM` data | Preserve code `ALRS` and update name in place. |
| Production credentials accidentally hardcoded | Use environment variables only. |
| Bootstrap silently creates weak owner credentials | Fail closed when production owner credentials are missing. |
| Super Admin becomes branch-scoped accidentally | Keep Super Admin `branch_id` nullable unless explicitly required. |
| Tests depend on old organization name | Update tests only if they assert display name. |

## Estimated Effort

| Work | Estimate |
| --- | --- |
| Bootstrap script/service | 0.5-1 day |
| Docker and env documentation | 0.5 day |
| Backend tests | 0.5-1 day |
| Verification | 0.5 day |

Total:

```text
1.5-3 engineering days
```

## Sprint Recommendation

Recommended sprint:

```text
Sprint 7.2 - Bootstrap And Organization Foundation
```

Do not combine this with the full SaaS onboarding UI. Keep the default
organization bootstrap small, deterministic, and production-safe.

## GO / NO-GO Recommendation

Default organization `Alluring Lens Studios`:

```text
GO
```

Reason:

- It can be implemented as idempotent bootstrap data.
- It does not require schema changes.
- It can preserve existing `ALRS` development data.
- It does not need to weaken tenant isolation.

Future SaaS Organization Onboarding module:

```text
GO WITH PREREQUISITES
```

Required prerequisites:

- Tenant-aware login decision.
- Organization Management frontend.
- Owner invite or secure password setup flow.
- Default branch creation workflow.
- Public Gallery sharing hardening plan.
- End-to-end tenant isolation tests.

