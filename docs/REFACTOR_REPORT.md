# Refactor Report

Date: 2026-06-10

Source: `docs/ARCHITECTURE_REVIEW.md`

## Summary

Implemented the architecture review recommendations while preserving the Sprint
1 API surface and response envelope. Existing endpoints remain available, list
responses still return arrays in `data`, and new pagination metadata is exposed
through `meta`.

## Security Changes

- Added environment validation for production JWT configuration.
- Kept local development defaults but fail non-local startup when
  `JWT_SECRET_KEY` is weak or left at the default value.
- Changed password hashing to SHA-256 pre-hash before bcrypt to avoid bcrypt's
  72-byte input truncation behavior.
- Added password strength validation for user create/update.
- Added login rate limiting backed by Redis with an in-process fallback for
  tests and local development.
- Added refresh token persistence in `refresh_token_sessions`.
- Added refresh token rotation and replay detection.
- Added `/api/v1/auth/logout` to revoke refresh tokens.
- Revoked active refresh sessions when a password changes or a user is
  deactivated.

## Authorization And RBAC Changes

- Added `AuthorizationContext` and tenant/branch-aware policy checks.
- Scoped organization, branch, and user reads/writes by actor organization and
  branch unless the actor has a platform role.
- Added role metadata: `is_platform` and `priority`.
- Prevented non-platform users from assigning platform roles.
- Prevented users from assigning roles above their own role priority.
- Preserved permission-code checks while adding resource-level checks in service
  operations.

## Data And PostgreSQL Changes

- Added Alembic migration `202606100002_harden_identity_security`.
- Added `refresh_token_sessions` table.
- Added `audit_logs` table.
- Added role hierarchy columns.
- Added PostgreSQL `pgcrypto` setup and server-side UUID defaults.
- Added PostgreSQL boolean server defaults.
- Added lower-case functional unique indexes for organization codes, branch
  codes, and user emails.
- Added PostgreSQL check constraints for non-empty trimmed identity values.
- Added application and PostgreSQL branch/user organization consistency checks.
- Normalized emails to lowercase and codes to uppercase in write paths.

## Clean Architecture Improvements

- Added application exception types and a FastAPI exception mapper.
- Moved authorization rules into `identity/policies.py` instead of keeping all
  RBAC behavior inside route dependencies.
- Added audit service for security-sensitive events.
- Added a typed API response schema for OpenAPI while preserving the existing
  response envelope.

## Scalability Changes

- Added page/page_size pagination to organization, branch, and user list
  endpoints.
- Added pagination metadata in `meta`.
- Added configurable SQLAlchemy pool sizing for PostgreSQL deployments.
- Replaced hard deletes with soft deactivation for organizations, branches, and
  users.

## Infrastructure And CI Changes

- Updated Docker image to run as a non-root user.
- Added `docker-compose.prod.yml` as a production-oriented Compose baseline.
- Kept `docker-compose.yml` backwards-compatible for local development.
- Updated GitHub Actions to start PostgreSQL and run `alembic upgrade head`.

## Tests Added

- Refresh token rotation and replay rejection.
- Logout refresh-token revocation.
- Password strength rejection.
- Tenant isolation for organization reads.
- Role escalation denial for platform roles.
- Cross-organization branch assignment rejection.
- Soft deactivation behavior.
- Pagination metadata on list endpoints.

## Verification

Commands run locally:

```bash
ruff check backend
python3 -m pytest
DATABASE_URL=sqlite+pysqlite:////private/tmp/alrscrm_refactor_migration.db alembic upgrade head
```

Results:

- Ruff: passed
- Pytest: 12 passed
- Alembic SQLite upgrade: passed

## Compatibility Notes

- Existing endpoints and request bodies remain supported.
- `DELETE` endpoints now deactivate identity records instead of physically
  deleting them.
- List endpoint `data` remains an array; `meta` was added for pagination.
- `/api/v1/auth/logout` is additive.

## Remaining Operational Work

- Run the new PostgreSQL migration in the deployment pipeline before rolling out
  API workers.
- Provide strong production secrets through the runtime environment.
- Decide whether audit logs should later be exported to a central log or SIEM.
