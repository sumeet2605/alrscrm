# Sprint 6 Release Cleanup

Cleanup date: 2026-06-11

Scope:

- Ruff cleanup only
- Formatting
- Import cleanup
- Type annotation cleanup
- Exception chaining cleanup
- Test formatting cleanup
- EDD audit documentation

No business logic, API contract, database schema behavior, RBAC behavior,
workflow state transition, domain rule, or audit event name change was
intentionally introduced.

## Violations Before

Initial command:

```bash
ruff check backend frontend --fix
```

Initial result:

```text
Found 93 errors.
12 fixed.
81 remaining.
```

Remaining violation categories after auto-fix:

- `E501` line too long
- `F821` undefined `GalleryUpgradeRequest` type references
- `F841` unused local variable
- `B904` missing exception chaining

## Violations After

Final command:

```bash
ruff check backend frontend
```

Final result:

```text
All checks passed!
```

Formatting command:

```bash
ruff format backend frontend
```

Final result:

```text
137 files left unchanged
```

## Files Changed

Ruff cleanup and manual fixes touched:

- `backend/alembic/versions/202606100004_create_family_domain.py`
- `backend/alembic/versions/202606100005_create_sales_pipeline.py`
- `backend/alembic/versions/202606100007_create_booking_fulfillment.py`
- `backend/alembic/versions/202606100010_add_gallery_selection_governance.py`
- `backend/alembic/versions/202606100011_create_gallery_upgrade_requests.py`
- `backend/alembic/versions/202606100012_harden_gallery_upgrade_requests_and_create_editing.py`
- `backend/app/bookings/repositories.py`
- `backend/app/core/config.py`
- `backend/app/editing/repositories.py`
- `backend/app/editing/services/editing_service.py`
- `backend/app/galleries/models/__init__.py`
- `backend/app/galleries/repositories.py`
- `backend/app/galleries/routes.py`
- `backend/app/galleries/services/gallery_service.py`
- `backend/app/identity/routes/branches.py`
- `backend/app/identity/routes/organizations.py`
- `backend/app/identity/routes/users.py`
- `backend/app/sales/repositories.py`
- `backend/tests/conftest.py`
- `backend/tests/test_bookings_api.py`
- `backend/tests/test_editing_api.py`
- `backend/tests/test_families_api.py`
- `backend/tests/test_galleries_selection.py`

Documentation created:

- `docs/EDD_AUDIT.md`
- `docs/SPRINT6_RELEASE_CLEANUP.md`

## Runtime Issues Found

No runtime regression was found from the Ruff cleanup.

Critical inspection completed for:

- `backend/app/galleries/models/__init__.py`
- `backend/app/galleries/repositories.py`
- `backend/app/galleries/services/gallery_service.py`
- `backend/app/editing/repositories.py`
- `backend/app/editing/services/editing_service.py`

Inspection result:

- `GalleryUpgradeRequest` references resolve through type-only imports and
  existing local runtime imports.
- Gallery authentication exception handling now preserves exception cause.
- The unused repository local in `submit_selection` was removed.
- Editing workflow state transitions remain unchanged.
- Editing RBAC and scope checks remain unchanged.
- Audit event names remain unchanged.

## Runtime Issues Fixed

Ruff cleanup fixed code-health issues only:

- Undefined type references for Ruff/static analysis.
- Missing exception chaining for gallery access token decoding.
- Unused local variable in gallery selection submission.
- Long-line and import-format violations.

No API behavior, migration semantics, RBAC behavior, or domain workflow behavior
was intentionally changed.

## EDD Audit Summary

EDD audit document:

- `docs/EDD_AUDIT.md`

Summary:

- EDD is fully wired for Family persistence, ORM, schemas, create/update APIs,
  list filtering, frontend form, frontend detail page, frontend list page, and
  generated OpenAPI types.
- EDD is partially implemented for observability because EDD changes are
  covered by `family.updated`, not a discrete EDD domain event.
- Missing future capabilities include EDD history, EDD-specific notifications,
  EDD dashboard/reminder workflow, and dedicated EDD range filter tests.

Recommended sprint:

- Keep current EDD support as-is.
- Add EDD lifecycle/history and notification work in a future Delivery
  Management sprint.

## Final Test Counts

Backend:

```text
python -m pytest backend/tests
39 passed, 13 warnings
```

Frontend:

```text
npm run test
17 files passed, 25 tests passed
```

Warnings:

- Existing Starlette/httpx deprecation warning.
- Existing deprecated `datetime.utcnow()` warnings in gallery tests.
- Existing Ant Design `act(...)` warning in `DashboardLayout.test.tsx`.

## Build Status

Frontend lint:

```text
npm run lint
passed
```

Frontend production build:

```text
npm run build
passed
```

Build warning:

- Existing Vite chunk-size warning remains.

## Migration Status

Docker rebuild and startup:

```text
docker compose up -d --build
passed
```

PostgreSQL Alembic upgrade:

```text
docker compose exec api alembic upgrade head
passed
```

## Release Readiness Verdict

Sprint 6 remains release-ready after cleanup.

Ruff is clean, backend tests pass, frontend checks pass, Docker rebuild passes,
and Alembic upgrade succeeds. No intentional functional behavior changes were
introduced.
