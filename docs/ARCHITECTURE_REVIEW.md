# ALRSCRM Architecture Review

Review date: 2026-06-10

Scope: full repository review of the current Sprint 1 implementation. This is a
review-only document; no application code was changed.

## Critical Issues

### 1. Default JWT Secret Is Production-Unsafe

`backend/app/core/config.py:18` defines `jwt_secret_key` with the default value
`change-this-secret-in-production`. If production starts without an explicit
environment override, every access and refresh token can be forged by anyone
who knows the repository.

Impact:
- Full account takeover for any known user id.
- RBAC bypass through forged tokens.
- No runtime failure makes the misconfiguration obvious.

Recommendation:
- Require `JWT_SECRET_KEY` in non-local environments.
- Enforce minimum length and entropy checks during settings validation.
- Fail application startup when the secret is missing or equals a known default.

### 2. Refresh Tokens Are Stateless And Cannot Be Revoked

Refresh tokens are created and validated only through JWT claims in
`backend/app/core/security.py:41-47` and `backend/app/auth/service.py:36-47`.
There is no refresh token table, token id (`jti`), rotation, reuse detection, or
logout/revocation path.

Impact:
- A leaked refresh token remains valid until expiry.
- Password changes or account compromise cannot invalidate existing sessions.
- Refresh token replay cannot be detected.

Recommendation:
- Persist refresh token sessions with hashed token ids, user id, expiry,
  revoked_at, created_by_ip, and user_agent.
- Rotate refresh tokens on every refresh.
- Revoke all sessions on password reset, user deactivation, and role changes
  that materially reduce privileges.

### 3. Multi-Tenant Authorization Is Missing

The data model includes `organization_id` and `branch_id`, but the services and
routes do not scope reads or writes by the authenticated user. For example,
`list_users()` returns every user in `backend/app/identity/services/user_service.py:12-13`,
`list_organizations()` returns every organization in
`backend/app/identity/services/organization_service.py:11-12`, and route handlers
do not pass tenant context from `current_user` into services.

Impact:
- Any user with broad read permissions can enumerate cross-tenant data.
- Any user with write permissions can mutate records in other organizations.
- The intended Owner and Branch Manager boundaries from the permission matrix
  are not enforced.

Recommendation:
- Introduce an authorization context object derived from the current user.
- Require every query to apply organization and branch scope unless the caller is
  a true platform role.
- Add integration tests proving cross-organization access is denied.

### 4. RBAC Is Only Coarse Permission Checking

`require_permissions()` checks only whether a user has a permission code in
`backend/app/api/deps.py:37-51`. It does not enforce resource ownership, branch
scope, organization scope, role hierarchy, or protected-role constraints. The
hard-coded `"Super Admin"` bypass in `backend/app/api/deps.py:44-45` is name
based and not bounded by tenant/platform semantics.

Impact:
- A Branch Manager can be modeled as having access but cannot be restricted to
  their branch.
- A user with `identity:users:write` can assign roles arbitrarily through
  `role_ids` in `backend/app/identity/schemas/user.py:19-21`.
- Protected roles can be escalated or altered unless prevented elsewhere.

Recommendation:
- Split authorization into permission checks plus resource policy checks.
- Add explicit policies such as `can_manage_user(actor, target_user)`.
- Prevent lower-privileged roles from assigning higher-privileged roles.
- Represent platform-level roles separately from tenant roles.

## Major Issues

### 1. Clean Architecture Boundaries Are Leaky

Service modules depend directly on SQLAlchemy sessions, ORM models, Pydantic
transport schemas, and FastAPI HTTP exceptions. Examples:
- `backend/app/identity/services/user_service.py:3-9`
- `backend/app/identity/services/organization_service.py:3-8`
- `backend/app/shared/exceptions/http.py`

Impact:
- Domain/application logic is coupled to FastAPI and SQLAlchemy.
- Business rules are difficult to test without database fixtures.
- Future background jobs or CLI workflows will reuse HTTP-specific failures.

Recommendation:
- Introduce application commands/use cases that accept plain command DTOs.
- Move persistence behind repository interfaces.
- Raise domain/application exceptions from services and map them to HTTP in the
  API layer.

### 2. Password Policy And Hashing Need Production Hardening

Passwords require only length validation in `backend/app/identity/schemas/user.py:20`
and `backend/app/identity/schemas/user.py:28`. There is no complexity policy,
breach list check, rate limiting, account lockout, or login audit. Bcrypt is
acceptable, but long passwords are not pre-hashed before bcrypt's 72-byte limit.

Impact:
- Weak passwords are accepted.
- Credential stuffing has no application-level friction.
- Long passwords may not behave as users expect because bcrypt truncates input.

Recommendation:
- Enforce a policy appropriate for staff accounts.
- Add login rate limiting backed by Redis.
- Consider Argon2id or bcrypt with SHA-256 pre-hashing.
- Record authentication audit events.

### 3. Startup Mutates Database State

The FastAPI lifespan calls `seed_identity(db)` on every startup in
`backend/app/main.py:17-27`. Database writes during web startup mix deployment,
migration, and runtime concerns.

Impact:
- Startup behavior depends on database write availability.
- Multiple app instances can concurrently seed during rollout.
- Seed failures are logged and ignored, potentially leaving RBAC incomplete.

Recommendation:
- Run seeding as an explicit release step after migrations.
- Keep startup read-only except for health checks and dependency initialization.
- Make missing baseline roles/permissions a failing readiness condition.

### 4. Deletes Are Hard Deletes

Organization, branch, and user services call `db.delete()` directly:
- `backend/app/identity/services/organization_service.py:49-52`
- `backend/app/identity/services/branch_service.py:56-59`
- `backend/app/identity/services/user_service.py:85-88`

Impact:
- Audit history and referential integrity will be fragile once CRM, sessions,
  payments, and production records are added.
- Deleting an organization can remove or orphan operational records depending on
  later relationships.

Recommendation:
- Prefer soft-delete or deactivate workflows for identity records.
- Restrict physical deletes to administrative maintenance operations.
- Add audit events for deactivation and role changes.

### 5. Pagination, Filtering, And Search Are Missing

List endpoints return all records:
- `backend/app/identity/services/user_service.py:12-13`
- `backend/app/identity/services/branch_service.py:11-12`
- `backend/app/identity/services/organization_service.py:11-12`

Impact:
- Unbounded memory and response size as data grows.
- No stable API contract for operational UI screens.
- Cross-tenant leaks become larger because every result is returned.

Recommendation:
- Add page/page_size or cursor pagination to all list endpoints.
- Add tenant-scoped filtering and deterministic ordering.
- Return pagination metadata in the response envelope.

### 6. PostgreSQL Schema Needs Stronger Constraints

The migration creates UUID columns but does not define database-side UUID
defaults in `backend/alembic/versions/202606100001_create_identity_access_tables.py`.
Defaults exist only in Python model mixins. Boolean columns are non-null but lack
server defaults. Email and code values are stored as raw strings without
normalization.

Impact:
- Direct inserts outside SQLAlchemy require explicit ids and booleans.
- Case variants can bypass intended uniqueness, e.g. `Owner@Example.com`.
- Seed and import scripts are more error-prone.

Recommendation:
- Use PostgreSQL `gen_random_uuid()` server defaults.
- Add server defaults for booleans.
- Use normalized lowercase columns, `citext`, or functional unique indexes for
  email and code fields.
- Add check constraints for trimmed non-empty values where appropriate.

### 7. User-Branch Consistency Is Not Enforced

`_ensure_user_refs()` verifies the organization and branch exist, but does not
verify that `branch.organization_id == user.organization_id` in
`backend/app/identity/services/user_service.py:32-36`.

Impact:
- A user can be assigned to an organization and a branch from another
  organization.
- Branch-level RBAC becomes unreliable.

Recommendation:
- Add application validation and a database-level composite foreign key or
  constraint strategy to ensure branch and organization consistency.
- Add tests for rejecting cross-organization branch assignment.

### 8. CI Does Not Run Migrations Or PostgreSQL Integration Tests

The workflow runs lint and SQLite-backed tests only in
`.github/workflows/ci.yml:20-27`. It does not start PostgreSQL, run Alembic
against PostgreSQL, or validate the Docker Compose startup path.

Impact:
- PostgreSQL-specific migration and constraint errors can reach deployment.
- SQLite tests can mask UUID, timezone, transaction, and constraint differences.

Recommendation:
- Add a PostgreSQL service container in CI.
- Run `alembic upgrade head`.
- Run integration tests against PostgreSQL in addition to fast unit tests.

## Minor Issues

### 1. Generated Python Cache Files Exist In The Workspace

`__pycache__` directories are present under `backend/app` and `backend/tests`.
They are ignored by `.gitignore`, but they add noise to local review and
artifact scanning.

Recommendation:
- Keep generated caches out of workspace snapshots and deployment contexts.

### 2. Docker Compose Uses Development Defaults

`docker-compose.yml:13-18` runs Uvicorn with `--reload` and bind-mounts source
code. `docker-compose.yml:22-25` also defines static local database credentials.

Recommendation:
- Keep this compose file explicitly local-only or split local and production
  compose definitions.
- Do not reuse `.env.example` as an operational env file outside local
  development.

### 3. Docker Image Runs As Root

`backend/Dockerfile` does not create or switch to a non-root user.

Recommendation:
- Add a dedicated non-root user and run the API process under it.

### 4. Response Envelope Is Untyped

`backend/app/api/responses.py` returns a plain dictionary. Route responses do
not declare response models.

Recommendation:
- Define a generic response schema or explicit response models per endpoint.
- Preserve the required envelope while keeping OpenAPI accurate.

### 5. Role And Permission Data Is Static Code

Roles and permissions are hard-coded in `backend/app/identity/seeds.py:5-41`.
This is acceptable for a first seed, but it lacks versioning and migration
semantics.

Recommendation:
- Treat permission changes as versioned data migrations.
- Keep role assignments configurable by tenant where appropriate.

## Missing Tests

- Cross-tenant isolation tests for organizations, branches, and users.
- Branch Manager scope tests proving branch-only access.
- Negative RBAC tests for users lacking `write` permissions.
- Role escalation tests for assigning `Super Admin` or `Owner`.
- Refresh token replay, expiry, inactive-user, and revoked-session tests.
- Password hashing and long-password behavior tests.
- Duplicate email/code tests, including case-insensitive variants.
- Cross-organization branch assignment rejection tests.
- Alembic migration tests against PostgreSQL.
- Delete/deactivation behavior tests.
- Pagination and filtering tests once implemented.
- Docker image smoke test and Compose startup test.

## Code Smells

- Route handlers repeat serialization boilerplate such as
  `ModelRead.model_validate(...).model_dump(mode="json")`.
- Service functions mix transaction control, validation, persistence, and
  HTTP-facing error semantics.
- Entity creation uses `Model(**payload.model_dump())`, which makes schema
  changes directly affect persistence behavior.
- `settings_dependency()` in `backend/app/api/deps.py:56-57` is currently unused.
- `RoleRead` nests permissions for role list responses, but user reads also
  include roles, making response depth likely to grow without explicit API
  design.

## Clean Architecture Violations

- Application services depend on infrastructure concerns (`Session`,
  SQLAlchemy models, and `IntegrityError`).
- Services depend on presentation-layer concerns through FastAPI `HTTPException`
  helpers.
- Pydantic request schemas act as application command objects.
- Persistence models are currently the domain model; there are no domain
  entities or value objects independent of the ORM.
- Authorization policy is implemented as an API dependency instead of a reusable
  application policy layer.

## Scalability Concerns

- Unbounded list queries and response payloads.
- No connection pool sizing or environment-based pool configuration in
  `backend/app/core/database.py:14`.
- No read/write query separation or repository abstraction for future reporting
  and operational dashboards.
- No audit/event stream for security-sensitive identity changes.
- No rate limiting despite Redis being part of the target stack.
- No background task model for future WhatsApp, follow-up, or notification
  workflows.

## PostgreSQL Modeling Issues

- Missing server-side UUID generation.
- Missing server defaults for booleans.
- Case-sensitive unique constraints on email and code fields.
- No `updated_at` database trigger; `onupdate` is ORM-side only.
- No explicit `ondelete` strategy for organization, branch, and user foreign
  keys.
- No uniqueness for branch email or phone if business rules require it.
- No check constraints for non-empty trimmed codes and names.
- `roles` and `permissions` are global; future tenant-customized roles will need
  either tenant scope or a separate role template model.

## RBAC Weaknesses

- Permissions are action-only and do not include resource scope.
- `Super Admin` bypass is string-name based.
- Role assignment is not constrained by the actor's authority.
- There is no protected-role policy for platform roles.
- Role and permission reads expose full permission structure to any user with
  read permissions, regardless of tenant or role hierarchy.
- No audit trail for role assignment, permission changes, or user activation
  changes.

## Recommended Refactors

1. Add environment validation that fails startup for insecure secrets and
   production-unsafe settings.
2. Introduce an application authorization layer with tenant and branch-aware
   policies.
3. Add repository interfaces for identity persistence and move SQLAlchemy access
   behind infrastructure adapters.
4. Replace service-level `HTTPException` usage with domain/application
   exceptions mapped by API exception handlers.
5. Implement refresh token persistence, rotation, revocation, and logout.
6. Add PostgreSQL-backed CI with Alembic migration execution.
7. Normalize email and code fields and add PostgreSQL constraints for case
   insensitive uniqueness.
8. Replace hard deletes with deactivation workflows and audit events.
9. Add pagination and filtering contracts for all list endpoints.
10. Split local Docker Compose from production deployment configuration.
11. Build a security test suite covering RBAC denial paths, tenant isolation,
    token lifecycle, and role escalation.
12. Move RBAC seed changes into versioned data migrations or a controlled seed
    runner executed during release, not during web startup.
