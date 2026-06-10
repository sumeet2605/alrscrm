# Sprint 6 Test Strategy

## Goals

- Prove the editing workflow works from Gallery selection through
  ready-for-delivery.
- Prove tenant, branch, RBAC, and editor ownership rules hold.
- Prove production frontend pages render meaningful states and call the API
  layer correctly.
- Keep tests focused on Sprint 6 scope only.

## Backend Tests

Current coverage:

- EditingJob auto-creation after Gallery selection submission.
- Editor assignment.
- Start editing.
- Submit review only after all selected photos are completed.
- Editor self-approval denial.
- Manager approval.
- Ready-for-delivery transition.
- Ready-for-delivery update denial.
- Editing metrics and editor dashboard responses.
- Cross-tenant EditingJob access denial.
- Gallery upgrade request branch scoping.
- Family one-to-one address update regression.

Primary test file:

- `backend/tests/test_editing_api.py`

Supporting regression file:

- `backend/tests/test_families_api.py`

## Frontend Tests

Current Sprint 6 coverage:

- Editing queue renders job rows.
- Production dashboard renders metrics.
- Editor dashboard renders workload metrics.
- Editing job detail page triggers ready-for-delivery action.
- Dashboard navigation includes Production routes.

Primary test files:

- `frontend/src/modules/production/EditingQueuePage.test.tsx`
- `frontend/src/modules/production/ProductionDashboardPage.test.tsx`
- `frontend/src/modules/production/EditorDashboardPage.test.tsx`
- `frontend/src/modules/production/EditingJobDetailPage.test.tsx`
- `frontend/src/layouts/DashboardLayout.test.tsx`

## Required Validation Commands

```bash
python -m pytest backend/tests
cd frontend
npm run lint
npm run test
npm run build
```

Docker migration validation:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

OpenAPI validation:

```bash
cd frontend
npm run generate:api-types
```

## Non-Blocking Test Debt

- Replace deprecated `datetime.utcnow()` in gallery test setup.
- Remove existing Ant Design `act(...)` warning from `DashboardLayout.test.tsx`.
- Add frontend tests for assign, start, submit review, approve, and reject modal
  flows on `EditingJobDetailPage`.
- Add explicit branch-crossing EditingJob tests in addition to tenant tests.
- Add negative API tests for non-Editor assignment attempts.
