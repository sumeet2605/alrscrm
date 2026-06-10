# Sprint 3.1 Completion Report

Sprint 3.1 hardened Sprint 3 only. No Sprint 4 modules were implemented.

## 1. Critical Issues Fixed

### Cross-Tenant FollowUp Mutations

Fixed.

Overdue follow-up aging now requires organization or branch scope before
updating records. A tenant-scoped user no longer mutates another tenant's
follow-ups through dashboard or follow-up reads.

### Cross-Branch FollowUp Mutations

Fixed.

Branch-scoped users age only follow-ups connected to opportunities in their
branch.

### Pipeline Truncation

Fixed.

The pipeline board no longer uses `page=1&page_size=100` from the list endpoint.
It now uses a dedicated scoped query and preserves the existing Kanban response
shape.

## 2. Major Issues Fixed

### KPI Deleted Opportunity Leakage

Fixed.

Follow-up KPI calculations now join through non-deleted opportunities only.

### Opportunity Edit Workflow

Fixed.

The existing edit action now opens a functional edit form on the opportunity
detail route.

### LostReason Drag Workflow

Fixed.

Dragging an opportunity to `LOST` now opens a LostReason modal before the stage
change is submitted.

### Database Guardrails

Added:

- Probability check constraint
- LOST requires LostReason check constraint
- PostgreSQL trigger protecting `BOOKED` opportunity business fields from direct
  updates

## 3. Tests Added

Backend:

- Cross-tenant follow-up aging regression test
- Cross-branch follow-up aging regression test
- Pipeline over-100-opportunities regression test
- KPI deleted-opportunity exclusion test
- Database probability and LOST-stage constraint test

Frontend:

- Opportunity edit workflow test
- LOST drag/drop LostReason modal test

## 4. Security Improvements

- Tenant-scoped overdue mutation prevents cross-tenant side effects.
- Branch-scoped overdue mutation prevents cross-branch side effects.
- Automatic missed follow-up transitions now produce audit events.
- KPI and follow-up reads exclude soft-deleted opportunities.

## 5. Performance Improvements

- Pipeline uses a dedicated query instead of a capped paginated list call.
- Pipeline query uses eager loading to avoid N+1 relationship fetching.
- Added scope and status/date indexes for common opportunity and follow-up
  dashboard access paths.

## 6. KPI Validation Results

Validated:

- Conversion Rate excludes deleted opportunities.
- Open Opportunities excludes deleted opportunities.
- Lost Opportunities excludes deleted opportunities.
- Booked Opportunities excludes deleted opportunities.
- Average Opportunity Value excludes deleted opportunities.
- Follow Up Compliance excludes follow-ups attached to deleted opportunities.

## 7. Remaining Technical Debt

- Read-time overdue follow-up aging remains a side effect. It is now scoped and
  audited, but a scheduled tenant-aware job would be cleaner.
- Backend generic `APIResponse` still limits generated frontend read DTOs.
- Audit logs are not a durable outbox.
- Pipeline is no longer capped, but future very high-volume usage should add
  explicit per-stage pagination.
- The frontend bundle still needs future code splitting.

## 8. Recommendation To Start Sprint 4

Sprint 4 can start after the Sprint 3.1 migration is applied and the green test
suite is confirmed in CI.

Recommended Sprint 4 entry conditions:

- Apply `202606100006_harden_sales_pipeline`.
- Confirm production seed commands still run before API startup.
- Confirm dashboard and opportunity workflows in a deployed environment.

Do not start Booking implementation until those checks pass.
