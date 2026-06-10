# Sprint 4 Completion Report

Sprint 4 implements Booking, Scheduling, and Photographer Assignment only.

Gallery, Editing, Delivery, Payments, WhatsApp, and AI were not implemented.

## 1. Files Created

Backend:

- `backend/app/bookings/*`
- `backend/alembic/versions/202606100007_create_booking_fulfillment.py`
- `backend/tests/test_bookings_api.py`

Frontend:

- `frontend/src/api/bookings.ts`
- `frontend/src/types/bookings.ts`
- `frontend/src/modules/bookings/*`

Docs:

- `docs/SPRINT4_BOOKING_DOMAIN.md`
- `docs/SPRINT4_DATABASE_DESIGN.md`
- `docs/SPRINT4_API_REFERENCE.md`
- `docs/SPRINT4_COMPLETION_REPORT.md`

## 2. Tables Added

- `packages`
- `package_addons`
- `bookings`
- `booking_items`
- `booking_item_addons`
- `shoot_schedules`
- `photographer_assignments`

## 3. APIs Added

- `POST /api/v1/bookings`
- `GET /api/v1/bookings`
- `GET /api/v1/bookings/{id}`
- `PUT /api/v1/bookings/{id}`
- `DELETE /api/v1/bookings/{id}`
- `GET /api/v1/bookings/metrics`
- `POST /api/v1/packages`
- `GET /api/v1/packages`
- `GET /api/v1/packages/{id}`
- `PUT /api/v1/packages/{id}`
- `POST /api/v1/addons`
- `GET /api/v1/addons`
- `PUT /api/v1/addons/{id}`
- `POST /api/v1/schedules`
- `GET /api/v1/schedules`
- `GET /api/v1/schedules/{id}`
- `PUT /api/v1/schedules/{id}`
- `POST /api/v1/assignments`
- `GET /api/v1/assignments`
- `DELETE /api/v1/assignments/{id}`

## 4. UI Pages Added

- `/bookings`
- `/bookings/new`
- `/bookings/:id`
- `/packages`
- `/schedules`
- `/schedules/assignments`

## 5. Tests Added

Backend:

- Booking lifecycle with package, addon, totals, schedule, assignment, and
  metrics
- Booking creation requires `BOOKED` Opportunity
- Sales Executive cannot assign photographers
- Cancelled bookings are read-only

Frontend:

- Booking list rendering from API layer
- Package and addon management rendering from API layer

## 6. Architecture Decisions

- Family remains the customer profile aggregate root.
- Opportunity remains the Sales aggregate.
- Booking is the Fulfillment aggregate root.
- Booking references Family and Opportunity by ID.
- Booking does not duplicate Family name, phone, email, or address.
- Package and PackageAddon are database-driven reference entities.
- Audit-backed domain events continue until an outbox is introduced.

## 7. Revenue Impact

Sprint 4 closes the operational gap after sales conversion:

- Booked opportunities become fulfillment records.
- Package and addon values are captured.
- Upcoming shoots can be scheduled and assigned.
- Booking KPIs expose booked revenue, upcoming shoots, completed shoots, and
  utilization.

This supports branch managers and owners in converting sales wins into
scheduled, staffed photography work.

## 8. Sprint 5 Dependencies

Sprint 5 can build on:

- `bookings.id`
- `booking_items.id`
- `shoot_schedules.id`
- `family_id`
- `opportunity_id`

Recommended next dependencies:

- Gallery should reference Booking or BookingItem.
- Editing should reference selected shoot/gallery outputs.
- Delivery should reference Gallery or edited deliverables.
- Payments should become a separate financial aggregate; do not overload
  `advance_received`.
