# Sprint 6 Completion Report

Sprint 6 implements Production Management for editing workflow only.

It starts after Gallery selection submission and ends when editing is ready for
future delivery.

Sprint 6 does not implement:

- Delivery
- Payments
- Invoices
- WhatsApp
- AI
- Event bus or outbox

## Implemented Scope

Completed:

- `EditingJob` aggregate root
- `EditingReview` child entity
- Automatic EditingJob creation when Gallery becomes `SELECTION_SUBMITTED`
- Editor assignment workflow
- Editing start workflow
- Review submission workflow
- Approval workflow
- Rejection workflow
- Ready-for-delivery workflow
- Production metrics API
- Editor dashboard API
- Production frontend pages
- RBAC seed updates
- Gallery upgrade request tenant and branch hardening
- Family address update bug fix discovered during Sprint 6 work

## Architecture Decisions

### EditingJob Aggregate Root

`EditingJob` is the Production Management aggregate root.

It references:

- `organization_id`
- `branch_id`
- `booking_id`
- `booking_item_id`
- `gallery_id`
- `assigned_editor_id`

It owns:

- `priority`
- `editing_status`
- `selected_photo_count`
- `completed_photo_count`
- `due_date`
- `started_at`
- `completed_at`
- `notes`
- `EditingReview`

### Rejected Design

Sprint 6 intentionally does not create one `EditingTask` row per selected
photo.

Reason:

- High row count
- Low operational value
- More complexity than the studio workflow needs

Progress is tracked through:

```text
completed_photo_count / selected_photo_count
```

### Boundary Rules

- Gallery remains the selection aggregate.
- EditingJob owns production state.
- Delivery remains future scope.
- Payments remain future scope.
- EditingJob does not duplicate Family customer profile fields.
- EditingJob does not own GalleryPhoto storage metadata.

## Backend Files Created

- `backend/app/editing/__init__.py`
- `backend/app/editing/enums.py`
- `backend/app/editing/models/__init__.py`
- `backend/app/editing/models/editing.py`
- `backend/app/editing/repositories.py`
- `backend/app/editing/routes.py`
- `backend/app/editing/schemas/__init__.py`
- `backend/app/editing/schemas/editing.py`
- `backend/app/editing/services/__init__.py`
- `backend/app/editing/services/editing_service.py`
- `backend/tests/test_editing_api.py`

## Backend Files Updated

- `backend/app/api/router.py`
- `backend/alembic/env.py`
- `backend/app/core/database.py`
- `backend/app/families/repositories.py`
- `backend/app/galleries/models/gallery.py`
- `backend/app/galleries/repositories.py`
- `backend/app/galleries/schemas/gallery.py`
- `backend/app/galleries/services/gallery_service.py`
- `backend/app/identity/policies.py`
- `backend/app/identity/seeds.py`
- `backend/tests/test_families_api.py`
- `backend/tests/test_identity_api.py`

## Migration Created

- `backend/alembic/versions/202606100012_harden_gallery_upgrade_requests_and_create_editing.py`

Migration changes:

- Adds `organization_id` and `branch_id` to `gallery_upgrade_requests`
- Backfills existing upgrade requests from `galleries`
- Adds tenant and branch foreign keys for upgrade requests
- Creates `editing_jobs`
- Creates `editing_reviews`
- Adds indexes for branch, editor, status, due date, booking, booking item, and
  gallery lookup

## APIs Added

Editing jobs:

- `GET /api/v1/editing/jobs`
- `POST /api/v1/editing/jobs`
- `GET /api/v1/editing/jobs/{job_id}`
- `PUT /api/v1/editing/jobs/{job_id}`
- `POST /api/v1/editing/jobs/{job_id}/assign-editor`
- `POST /api/v1/editing/jobs/{job_id}/start`
- `POST /api/v1/editing/jobs/{job_id}/submit-review`
- `POST /api/v1/editing/jobs/{job_id}/approve`
- `POST /api/v1/editing/jobs/{job_id}/reject`
- `POST /api/v1/editing/jobs/{job_id}/ready-for-delivery`

Metrics:

- `GET /api/v1/editing/metrics`
- `GET /api/v1/editing/my-work`

## Permissions Added

Seeded permissions:

- `galleries:reopen`
- `editing:view`
- `editing:create`
- `editing:update`
- `editing:assign`
- `editing:review`
- `editing:approve`
- `editing:dashboard`

Role behavior:

- `Super Admin`: all editing permissions
- `Organization Admin`: all editing permissions
- `Owner`: all editing permissions, retained for backward compatibility
- `Branch Manager`: all editing permissions within branch scope
- `Editor`: view, update, review, and dashboard access only
- `Editor` cannot approve own work

## Business Rules Implemented

- EditingJob auto-creates when Gallery reaches `SELECTION_SUBMITTED`.
- Manual EditingJob creation requires a submitted Gallery.
- One EditingJob per Gallery.
- Default priority is `NORMAL`.
- Default status is `PENDING`.
- Selected photo count is captured from current favorites.
- Completed photo count starts at `0`.
- Due date is calculated from selection submission date and priority:
  - `LOW`: +10 days
  - `NORMAL`: +7 days
  - `HIGH`: +3 days
  - `URGENT`: +1 day
- Managers may override due date.
- Editor assignment requires an active user with `Editor` role.
- Cannot start a job before editor assignment.
- Cannot submit for review until completed count equals selected count.
- Cannot mark ready for delivery unless approved.
- Jobs in `READY_FOR_DELIVERY` are read-only.
- Editor cannot approve or reject their own assigned job.

## Audit Events Added

Audit-backed events:

- `editing.job_created`
- `editing.editor_assigned`
- `editing.started`
- `editing.review_submitted`
- `editing.approved`
- `editing.rejected`
- `editing.ready_for_delivery`

No outbox or event bus was added.

## Metrics Implemented

`GET /api/v1/editing/metrics` returns:

- Pending Jobs
- Assigned Jobs
- In Progress Jobs
- Ready For Review
- Ready For Delivery
- Overdue Jobs
- Average Editing TAT
- Average Review TAT
- Jobs By Editor
- Jobs By Priority
- Jobs By Service Type
- Photos Edited This Month

`GET /api/v1/editing/my-work` returns:

- Assigned Jobs
- Due Today
- Overdue
- Completed This Week
- Current Workload

## Frontend Files Created

- `frontend/src/api/editing.ts`
- `frontend/src/types/editing.ts`
- `frontend/src/modules/production/ProductionDashboardPage.tsx`
- `frontend/src/modules/production/EditingQueuePage.tsx`
- `frontend/src/modules/production/EditingJobDetailPage.tsx`
- `frontend/src/modules/production/EditorDashboardPage.tsx`
- `frontend/src/modules/production/editingOptions.ts`
- `frontend/src/modules/production/EditingQueuePage.test.tsx`

## Frontend Files Updated

- `frontend/src/routes/AppRoutes.tsx`
- `frontend/src/routes/routePermissions.ts`
- `frontend/src/routes/routePermissions.test.ts`
- `frontend/src/layouts/DashboardLayout.tsx`
- `frontend/src/layouts/DashboardLayout.test.tsx`

## Frontend Routes Added

- `/production`
- `/production/editing`
- `/production/editing/:jobId`
- `/production/editor-dashboard`

Navigation added:

```text
Production
  Editing Queue
  Editor Dashboard
  Production Dashboard
```

## Documentation Created Or Updated

- `docs/SPRINT6_ARCHITECTURE_REVIEW.md`
- `docs/SPRINT6_EDITING_DOMAIN.md`
- `docs/EDITING_AGGREGATE_DIAGRAM.md`
- `docs/EDITING_EVENT_MAP.md`
- `docs/SPRINT6_COMPLETION_REPORT.md`

## Additional Fix Included

During Sprint 6 work, family update failures were reported from Docker logs:

```text
duplicate key value violates unique constraint "family_addresses_family_id_key"
```

Fix:

- Existing `FamilyAddress` rows are now updated in place instead of replacing
  the one-to-one row with a new insert.

Regression test:

- `backend/tests/test_families_api.py`

## Verification Status

Originally verified during implementation:

```bash
python -m pytest backend/tests/test_families_api.py
```

Result:

```text
3 passed
```

Final Sprint 6 readiness verification:

```bash
python -m pytest backend/tests
npm run lint
npm run test
npm run build
```

Results:

```text
Backend tests: 39 passed, 13 warnings
Frontend lint: passed
Frontend tests: 16 files passed, 24 tests passed
Frontend build: passed
```

Docker and migration verification:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

Result:

```text
Docker rebuild and restart: passed
Alembic PostgreSQL upgrade: passed
```

OpenAPI TypeScript types were regenerated:

```bash
cd frontend
npm run generate:api-types
```

## Known Follow-Ups

- Consider startup validation for editing permissions after seed execution.
- Reduce the frontend production bundle size through route-level code splitting.
- Resolve the existing Ant Design `act(...)` test warning in
  `DashboardLayout.test.tsx`.
- Replace deprecated `datetime.utcnow()` usage in gallery tests.

## Sprint 6 Status

Sprint 6 implementation is functionally present in the repository, including
the aggregate, APIs, frontend routes, metrics, RBAC seeds, and core workflow.

Sprint 6 is release-ready for the editing workflow after the final validation
pass documented in `docs/SPRINT6_RELEASE_READINESS.md`.
