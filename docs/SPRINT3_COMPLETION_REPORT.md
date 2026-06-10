# Sprint 3 Completion Report

## Files Created

- `backend/app/sales/*`
- `backend/alembic/versions/202606100005_create_sales_pipeline.py`
- `backend/scripts/seed_sales.py`
- `backend/tests/test_sales_api.py`
- `frontend/src/api/sales.ts`
- `frontend/src/types/sales.ts`
- `frontend/src/modules/sales/*`
- `docs/SPRINT3_ARCHITECTURE_DECISIONS.md`
- `docs/SPRINT3_OPPORTUNITY_DOMAIN.md`
- `docs/SPRINT3_DATABASE_DESIGN.md`
- `docs/SPRINT3_API_REFERENCE.md`
- `docs/SPRINT3_COMPLETION_REPORT.md`

## Tables Added

- `opportunities`
- `followups`
- `opportunity_notes`
- `opportunity_stage_history`
- `lost_reasons`

## APIs Added

- `POST /api/v1/opportunities`
- `GET /api/v1/opportunities`
- `GET /api/v1/opportunities/{id}`
- `PUT /api/v1/opportunities/{id}`
- `DELETE /api/v1/opportunities/{id}`
- `GET /api/v1/opportunities/pipeline`
- `GET /api/v1/opportunities/metrics`
- `POST /api/v1/followups`
- `GET /api/v1/followups`
- `PUT /api/v1/followups/{id}`
- `POST /api/v1/opportunities/{id}/notes`
- `GET /api/v1/opportunities/{id}/notes`
- `GET /api/v1/opportunities/{id}/history`
- `GET /api/v1/lost-reasons`

## UI Pages Added

- `/sales`
- `/sales/opportunities`
- `/sales/opportunities/new`
- `/sales/opportunities/:id`

## Tests Added

- Backend API tests for Opportunity CRUD, pipeline, lost reason validation,
  booked read-only behavior, follow-ups, metrics, stage history, and role access.
- Frontend Sales dashboard rendering test.

## Architecture Decisions

- Family remains the customer profile aggregate root.
- Opportunity references Family by `family_id`.
- FollowUp, OpportunityNote, and OpportunityStageHistory are Opportunity-owned child entities.
- LostReason is a database-driven Sales reference entity.
- Booking, Gallery, and Payment remain future aggregates.
- Sprint 3 domain events are audit-backed; no outbox exists yet.

## Revenue Impact Analysis

Sprint 3 targets the lead leakage path where package-sent leads go silent. The
new pipeline makes every opportunity visible, assigns ownership, tracks stage,
and exposes missed follow-ups. This supports the target move from 6 bookings per
month toward 15+ bookings per month at an average value of Rs 20,000 by reducing
untracked follow-up loss.

## Sprint 4 Dependencies

- Booking aggregate should be created from or linked to `BOOKED` Opportunities.
- Booking must reference `family_id` and `opportunity_id`.
- Activity timeline should read audit-backed sales events or a future outbox.
- Payment and Gallery modules must reference Family and future Booking without duplicating profile data.
