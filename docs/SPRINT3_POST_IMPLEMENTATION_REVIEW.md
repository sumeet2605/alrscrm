# Sprint 3 Post Implementation Review

Reviewed scope:

- Sprint 1 Identity and Access
- Sprint 2 Family domain
- Sprint 3 Sales Opportunity pipeline
- Backend APIs, database schema, RBAC, frontend architecture, tests, security,
  scalability, and DDD boundaries

Validated implementation areas:

- Backend models, schemas, services, repositories, routes, migrations, seeds,
  and tests
- Frontend API layer, route protection, sales pages, dashboard integration, and
  tests
- Current OpenAPI-driven frontend type usage

## Executive Validation

| Requirement | Status | Notes |
| --- | --- | --- |
| Opportunity does not duplicate Family data | Passed | `Opportunity` stores `family_id`; Family contact fields are only returned through read summaries. |
| FollowUp remains owned by Opportunity | Passed with caveat | `FollowUp` is scoped through parent `Opportunity`; top-level follow-up routes are workflow endpoints, not aggregate ownership. |
| LostReason is database-driven | Passed | `LostReason` is a table seeded through sales seed logic and exposed through a read API. |
| OpportunityStageHistory is populated correctly | Passed | Creation and stage changes create history rows. Non-stage edits correctly do not create stage history. |
| BOOKED opportunities become read-only | Passed | Service blocks opportunity update/delete, follow-up create/update, and note creation for booked opportunities. |
| Multi-tenant boundaries are enforced | Partially failed | Normal reads/writes are scoped, but overdue follow-up marking mutates records globally. |
| Branch-level access control is enforced | Partially passed | Normal service queries enforce branch scope, but overdue follow-up mutation is not branch-scoped. |
| Dashboard KPI calculations are correct | Failed | Follow-up KPI queries include follow-ups from soft-deleted opportunities. |

## Critical Issues

### 1. Overdue Follow-Up Marking Mutates Data Across Tenants

`backend/app/sales/repositories.py` updates all overdue pending follow-ups in
`mark_overdue_followups_missed()` without organization or branch filters. The
method is called from `SalesService.list_followups()` and
`SalesService.get_metrics()` before applying the caller's tenant and branch
scope.

Impact:

- A user from one tenant can trigger writes against another tenant's follow-ups.
- Read endpoints have hidden write side effects.
- Branch isolation is bypassed for status mutation.
- No audit event is written for these automatic `MISSED` transitions.

Recommendation:

- Pass scoped organization and branch filters into overdue marking.
- Prefer a scheduled tenant-aware job or explicit application service method.
- Record audit-backed `followup.missed` events for automatic transitions.
- Add regression tests proving one tenant or branch cannot mutate another
  tenant or branch's follow-ups.

### 2. Pipeline Board Silently Drops Opportunities After 100 Rows

`SalesService.get_pipeline()` calls `list_opportunities()` with `page=1` and
`page_size=100`, then groups only those rows by stage.

Impact:

- The pipeline can silently hide valid opportunities once a branch has more
  than 100 matching records.
- Stage counts and board contents can diverge from list and dashboard metrics.
- Sales users may miss active opportunities and follow-ups.

Recommendation:

- Implement a dedicated repository query for pipeline grouping.
- Either return all active opportunities grouped by stage or paginate per stage.
- Add tests for more than 100 opportunities.

## Major Issues

### 1. Follow-Up KPI Counts Include Soft-Deleted Opportunities

`SalesRepository.aggregate_counts()` filters soft-deleted opportunities for
opportunity metrics, but the follow-up query joins `Opportunity` without
filtering `Opportunity.deleted_at.is_(None)`.

Impact:

- Pending, missed, completed, and due follow-up metrics can include deleted
  opportunities.
- Follow Up Compliance can be lower or higher than the visible active pipeline
  state.

Recommendation:

- Add `Opportunity.deleted_at.is_(None)` to all follow-up KPI queries.
- Add tests covering metrics before and after opportunity soft delete.

### 2. Frontend Opportunity Edit Flow Is Incomplete

The Opportunity list exposes an edit action that navigates to
`/sales/opportunities/:id?edit=1`, but the detail page does not implement an
edit form or process the `edit` query parameter.

Impact:

- Users see an edit affordance that does not edit the opportunity.
- Backend supports opportunity update, but the frontend does not expose the full
  workflow.

Recommendation:

- Add an edit mode to the detail page or create a dedicated edit page.
- Reuse the create form with update behavior where practical.
- Include regression tests for opening and saving an opportunity edit.

### 3. Dragging An Opportunity To LOST Cannot Collect LostReason

The sales board allows stage changes through drag and drop. Moving an
opportunity to `LOST` sends only `current_stage: "LOST"`, but the backend
correctly requires `lost_reason_id`.

Impact:

- Dragging to `LOST` fails unless the opportunity already has a lost reason.
- Users cannot complete a core loss workflow from the board.

Recommendation:

- Show a LostReason selection modal before submitting a stage change to `LOST`.
- Keep the backend validation unchanged.
- Add frontend tests for the lost-stage interaction.

### 4. Sales Seed Validation Is Not Part Of Application Startup

Docker startup runs `seed_sales.py`, but FastAPI lifespan validation only checks
identity seed data. A non-Docker startup path can run without LostReason seed
values.

Impact:

- Sprint 3 can boot with an empty LostReason catalog.
- Opportunity loss workflow becomes unusable until manual seeding is performed.

Recommendation:

- Add startup validation for required sales reference data.
- Keep seed execution idempotent.
- Document local and production seed requirements.

### 5. Database Constraints Do Not Fully Protect Sales Invariants

Important invariants are enforced in service code but not protected by database
constraints.

Examples:

- Probability range is not constrained to `0..100`.
- `LOST` does not require `lost_reason_id` at the database level.
- Stage, type, and status values rely on application enum serialization.
- Opportunity and Family branch consistency is service-enforced, not
  database-enforced.

Impact:

- Direct imports, scripts, or future services can create invalid state.
- Data repair becomes harder as modules expand.

Recommendation:

- Add check constraints for probability and status/stage fields.
- Consider a constraint or trigger for `LOST` requiring `lost_reason_id`.
- Keep service validation as the primary business guard, but harden persistence
  for non-API writes.

## Minor Issues

### 1. Follow-Up Routes Can Obscure Aggregate Ownership

Top-level `/api/v1/followups` routes are acceptable for workflow convenience,
and the service correctly scopes through the parent opportunity. The API shape,
however, can make `FollowUp` appear to be an aggregate root.

Recommendation:

- Document that follow-up routes are workflow projections over Opportunity-owned
  child entities.
- Keep all write validation routed through Opportunity ownership checks.

### 2. API Response Envelope Weakens Generated Frontend Types

The generic `APIResponse` shape limits how precisely generated OpenAPI types
represent response payloads.

Recommendation:

- Use concrete response models per endpoint where practical.
- Continue using generated frontend types, but avoid relying on `unknown` or
  broad casts in API adapters.

### 3. Automatic MISSED Status Uses Read-Time Mutation

The system currently changes overdue follow-ups during list and metric reads.
Even after scoping is fixed, read-time mutation makes behavior harder to reason
about.

Recommendation:

- Move status aging to an explicit command, background job, or scheduled task.
- If read-time aging remains, make the side effect explicit in service naming
  and tests.

### 4. Frontend Sales Pages Are Growing Large

Sales dashboard, opportunity list, and detail pages combine data fetching,
permissions, layout, interaction logic, and presentation.

Recommendation:

- Extract focused components for KPI cards, pipeline columns, lost reason
  selection, follow-up panels, and opportunity forms.
- Keep API orchestration in hooks or module-level query helpers.

## Technical Debt

- Domain behavior remains concentrated in services and repositories rather than
  aggregate methods.
- Audit logs are used as domain event records, but there is still no outbox or
  asynchronous event bus.
- Stage history is append-only through service methods, but not protected
  against direct writes.
- Dashboard metrics are calculated through ad hoc repository queries instead of
  a dedicated reporting/query service.
- Frontend role checks rely on role names for some UI behavior; backend
  permissions remain authoritative.
- Current tests cover happy paths and key RBAC cases, but cross-tenant and
  branch-isolation regression coverage is not deep enough.

## Refactoring Recommendations

### Backend

1. Scope `mark_overdue_followups_missed()` by organization and branch, or move
   it to a tenant-aware scheduled job.
2. Fix follow-up KPI queries to exclude soft-deleted opportunities.
3. Replace the pipeline board query with a dedicated grouped query that does
   not truncate at 100 records.
4. Add sales reference-data validation to startup checks.
5. Add database check constraints for high-value invariants.
6. Add integration tests for:
   - Cross-tenant opportunity access
   - Cross-branch opportunity access
   - Cross-tenant follow-up status aging
   - Metrics excluding deleted opportunities
   - Pipeline behavior above 100 opportunities
   - Lost stage requiring LostReason
   - Booked opportunity read-only behavior across opportunity, follow-up, and
     note APIs

### Frontend

1. Implement the opportunity edit workflow behind the existing edit action.
2. Add LostReason selection before moving opportunities to `LOST`.
3. Add tests for sales list filters, opportunity creation, opportunity editing,
   LOST conversion, follow-up completion, and protected sales routes.
4. Split large sales pages into smaller module components and hooks.
5. Keep generated OpenAPI types as the source of truth for request and response
   contracts.

### Architecture

1. Keep Family as the owner of customer profile data.
2. Keep Opportunity as the Sales aggregate root.
3. Keep FollowUp as an Opportunity-owned child entity.
4. Keep LostReason as Sales-owned reference data.
5. Do not introduce Booking, Gallery, or Payment state into Opportunity.
6. Introduce a proper outbox before treating audit events as integration events.

## Sprint Validation Summary

Sprint 1 Identity remains structurally sound. RBAC permissions are defined,
seeded, and enforced at route boundaries, with branch scope applied in services.

Sprint 2 Family remains the correct customer profile aggregate. Sprint 3
correctly references Family rather than duplicating name, phone, or email in
Opportunity persistence.

Sprint 3 Opportunity is directionally aligned with the approved architecture:
Opportunity is the sales aggregate root, FollowUp is child-owned, LostReason is
database-driven, and booked opportunities are read-only. The main issues to
address before scaling Sprint 3 are tenant-safe follow-up status aging, pipeline
query correctness, KPI filtering, and completing the frontend edit/lost
workflows.
