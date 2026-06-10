# Sprint 3.1 Hardening

Sprint 3.1 closes the production-readiness findings from
`docs/SPRINT3_POST_IMPLEMENTATION_REVIEW.md`.

No Sprint 4 features were added. Booking, Scheduling, Payments, and Gallery
remain out of scope.

## Security Hardening

### Cross-Tenant Follow-Up Aging

Overdue follow-up aging is now scope-aware.

Changes:

- `mark_overdue_followups_missed()` requires organization or branch scope before
  mutating rows.
- Follow-up aging joins through `Opportunity` and excludes soft-deleted
  opportunities.
- Service methods pass caller scope before aging overdue follow-ups.
- Platform-wide reads no longer silently mutate every tenant's follow-ups.
- Automatic missed transitions now create `followup.missed` audit events.

Result:

- Tenant users cannot mutate another tenant's overdue follow-ups.
- Branch-scoped users cannot mutate another branch's overdue follow-ups.

### Cross-Branch Follow-Up Aging

Branch Manager access remains branch-specific.

Changes:

- Existing branch scoping is applied before follow-up aging.
- Branch-scoped callers attempting to pass a different branch still receive a
  forbidden response through existing scope validation.

## Pipeline Hardening

The pipeline board no longer uses the first 100 opportunities from the paginated
list endpoint.

Changes:

- Added a dedicated repository query for pipeline opportunities.
- Query excludes soft-deleted opportunities.
- Query applies organization and branch scope.
- Query eager-loads scalar relationships and child collections to avoid N+1
  behavior.
- Existing Kanban response shape is preserved.

## KPI Hardening

Dashboard metrics now exclude soft-deleted opportunities from both opportunity
and follow-up calculations.

Validated metrics:

- Conversion Rate
- Open Opportunities
- Lost Opportunities
- Booked Opportunities
- Average Opportunity Value
- Follow Up Compliance
- Pending Follow Ups
- Missed Follow Ups

Follow Up Compliance remains:

```text
Completed Due Follow Ups / Total Due Follow Ups
```

When there are no due follow-ups, compliance remains `100`.

## Frontend Workflow Hardening

### Opportunity Edit

The existing edit action now opens a functional edit mode on the opportunity
detail route.

Implemented:

- Edit form on `/sales/opportunities/:id?edit=1`
- Validation for required fields and probability range
- LostReason validation when stage is `LOST`
- Success notification
- Query invalidation for detail, list, and sales dashboard data

### Lost Reason Drag Workflow

Dragging an opportunity to `LOST` now opens a modal before submitting the stage
change.

Implemented:

- LostReason selection modal
- Optional stage-change notes
- Required LostReason validation
- Stage update submitted only after LostReason is selected

## Database Hardening

Added migration:

- `backend/alembic/versions/202606100006_harden_sales_pipeline.py`

Database protections:

- `ck_opportunity_probability_range`
- `ck_opportunity_lost_requires_reason`
- PostgreSQL trigger preventing direct mutation of `BOOKED` opportunity business
  fields

Indexes added:

- `ix_opportunities_scope_stage_created`
- `ix_opportunities_scope_deleted`
- `ix_followups_status_due`

## Performance Review

### Opportunity Queries

List queries remain paginated and scoped by organization and branch. Existing
filters continue to use indexed columns for stage, type, assigned user, family,
and expected booking date.

### Pipeline Queries

Pipeline now uses a dedicated query instead of a paginated list call. The query
uses eager loading to avoid per-card relationship fetches.

### Follow-Up Dashboard Queries

Follow-up list and aging queries now join through active opportunities and apply
scope filters.

### Lost Analytics

Lost analytics continues to use the pipeline data already loaded for the board.
No additional backend query was introduced.

### KPI Queries

KPI queries now filter deleted opportunities consistently for both opportunity
and follow-up calculations.

## Remaining Technical Debt

- Read-time overdue aging still has a write side effect, although it is now
  scoped and audited.
- Backend response models still use a generic API envelope, limiting generated
  frontend read DTO precision.
- Audit events are not a durable outbox.
- Pipeline endpoint remains unpaginated to preserve current Kanban behavior;
  future high-volume branches may need per-stage pagination.
