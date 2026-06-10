# Sprint 6 Validation Report

Validation date: 2026-06-10

Scope:

- Production Management editing workflow
- Gallery selection to EditingJob creation
- Editing API workflow and RBAC
- Production frontend pages
- OpenAPI TypeScript generation
- Docker startup and PostgreSQL migration

## Commands Run

| Area | Command | Result |
| --- | --- | --- |
| Backend tests | `python -m pytest backend/tests` | Passed: 39 tests |
| Editing focused tests | `python -m pytest backend/tests/test_editing_api.py` | Passed: 3 tests |
| Frontend type/lint | `npm run lint` from `frontend/` | Passed |
| Frontend tests | `npm run test` from `frontend/` | Passed: 16 files, 24 tests |
| Frontend build | `npm run build` from `frontend/` | Passed |
| Docker rebuild | `docker compose up -d --build` | Passed |
| PostgreSQL migration | `docker compose exec api alembic upgrade head` | Passed |
| OpenAPI generation | `npm run generate:api-types` from `frontend/` | Passed |

## Required Sprint 6 Test Coverage

| Scenario | Status | Location |
| --- | --- | --- |
| Gallery submitted creates EditingJob | Covered | `backend/tests/test_editing_api.py` |
| Editor assigned, started, reviewed, approved, ready for delivery | Covered | `backend/tests/test_editing_api.py` |
| Editor self approval denied | Covered | `backend/tests/test_editing_api.py` |
| Ready for delivery update attempt denied | Covered | `backend/tests/test_editing_api.py` |
| Cross-tenant EditingJob access denied | Covered | `backend/tests/test_editing_api.py` |

## Fixes Made During Validation

- Ready-for-delivery EditingJob update now returns `400 Bad Request`.
- Cross-tenant EditingJob access regression coverage was added.
- Public gallery favorite button now has an accessible label.
- Public gallery test was updated for the optional access token argument.
- Production dashboard, editor dashboard, editing queue, and editing detail
  pages now expose explicit error states.
- Production frontend tests were added for dashboard metrics and detail actions.
- Vitest UI timeout was raised to 15 seconds for Ant Design interaction tests.
- OpenAPI generated files were refreshed with Sprint 6 editing contracts.

## Warnings

- Backend tests emit one Starlette/httpx deprecation warning.
- Gallery tests still use deprecated `datetime.utcnow()` in test setup.
- Frontend tests emit an existing Ant Design `act(...)` warning from
  `DashboardLayout.test.tsx`.
- Frontend build emits a Vite chunk-size warning for the main bundle.

## Validation Outcome

Sprint 6 validation passed. Remaining items are non-blocking technical debt and
are documented in `docs/SPRINT6_TECH_DEBT.md`.
