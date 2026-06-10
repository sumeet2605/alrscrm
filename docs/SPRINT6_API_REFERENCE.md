# Sprint 6 API Reference

All routes are under `/api/v1` and use the existing API response envelope.

## Editing Job Endpoints

| Method | Path | Permission | Purpose |
| --- | --- | --- | --- |
| `GET` | `/editing/jobs` | `editing:view` | List editing jobs with pagination and filters. |
| `POST` | `/editing/jobs` | `editing:create` | Manually create an EditingJob for a submitted Gallery. |
| `GET` | `/editing/jobs/{job_id}` | `editing:view` | Read one scoped EditingJob. |
| `PUT` | `/editing/jobs/{job_id}` | `editing:update` | Update priority, status, completed count, due date, or notes. |
| `POST` | `/editing/jobs/{job_id}/assign-editor` | `editing:assign` | Assign an active Editor user. |
| `POST` | `/editing/jobs/{job_id}/start` | `editing:update` | Move an assigned or rejected job into progress. |
| `POST` | `/editing/jobs/{job_id}/submit-review` | `editing:review` | Submit completed editing work for review. |
| `POST` | `/editing/jobs/{job_id}/approve` | `editing:approve` | Approve a job ready for review. |
| `POST` | `/editing/jobs/{job_id}/reject` | `editing:approve` | Reject a job ready for review. |
| `POST` | `/editing/jobs/{job_id}/ready-for-delivery` | `editing:approve` | Mark an approved job ready for future delivery. |
| `GET` | `/editing/metrics` | `editing:dashboard` | Return production dashboard metrics. |
| `GET` | `/editing/my-work` | `editing:view` | Return current editor workload metrics. |

## Request Models

`EditingJobCreate`:

- `gallery_id`: required UUID
- `priority`: optional `LOW`, `NORMAL`, `HIGH`, `URGENT`; default `NORMAL`
- `due_date`: optional date
- `assigned_editor_id`: optional UUID
- `notes`: optional text, max 5000 characters

`EditingJobUpdate`:

- `priority`: optional
- `editing_status`: optional, but `READY_FOR_DELIVERY` must use the workflow
  endpoint
- `completed_photo_count`: optional integer, minimum `0`
- `due_date`: optional date
- `notes`: optional text, max 5000 characters

`EditingAssignEditor`:

- `assigned_editor_id`: required UUID
- `due_date`: optional date

`EditingReviewCreate`:

- `review_notes`: optional text, max 5000 characters

## Response Models

`EditingJobRead` includes:

- IDs: `id`, `organization_id`, `branch_id`, `booking_id`, `booking_item_id`,
  `gallery_id`, `assigned_editor_id`
- State: `priority`, `editing_status`, `selected_photo_count`,
  `completed_photo_count`, `due_date`, `started_at`, `completed_at`, `notes`
- Context: `gallery_name`, `booking_number`, `family_name`, `service_type`
- Related data: `assigned_editor`, `reviews`

`EditingMetricsRead` includes:

- `pending_jobs`
- `assigned_jobs`
- `in_progress_jobs`
- `ready_for_review`
- `ready_for_delivery`
- `overdue_jobs`
- `average_editing_tat`
- `average_review_tat`
- `jobs_by_editor`
- `jobs_by_priority`
- `jobs_by_service_type`
- `photos_edited_this_month`

`EditingDashboardRead` includes:

- `assigned_jobs`
- `due_today`
- `overdue`
- `completed_this_week`
- `current_workload`

## Business Rules

- Manual creation requires Gallery status `SELECTION_SUBMITTED`.
- Gallery submission auto-creates one EditingJob per Gallery.
- EditingJob is unique by `gallery_id`.
- Assigned editor must be an active user with the `Editor` role.
- A job cannot start until an editor is assigned.
- Review submission requires `completed_photo_count == selected_photo_count`.
- Approval and rejection require status `READY_FOR_REVIEW`.
- An assigned editor cannot approve or reject their own job.
- Ready-for-delivery requires status `APPROVED`.
- Ready-for-delivery jobs are read-only for update attempts.

## Error Behavior

- `400`: invalid workflow command such as updating a ready-for-delivery job.
- `403`: permission, tenant, branch, or editor-assignment scope violation.
- `404`: resource not found within the caller scope.
- `409`: business-state conflict such as starting an unassigned job.
- `422`: schema validation failure.

## Generated Types

Generated OpenAPI files:

- `frontend/src/types/generated/openapi-schema.json`
- `frontend/src/types/generated/openapi.ts`

Regeneration command:

```bash
cd frontend
npm run generate:api-types
```
