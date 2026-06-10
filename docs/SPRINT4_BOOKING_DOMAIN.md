# Sprint 4 Booking Domain

Sprint 4 introduces Booking as a Fulfillment aggregate. It does not implement
Gallery, Editing, Delivery, Payments, WhatsApp, or AI.

## Aggregate Boundary

`Booking` is the aggregate root for fulfillment after sales conversion.

Booking owns:

- `BookingItem`
- `BookingItemAddon`
- `ShootSchedule`
- `PhotographerAssignment`

Booking references:

- `Family` by `family_id`
- `Opportunity` by `opportunity_id`
- `Organization` and `Branch` for tenant and branch scope
- `User` for photographer assignments

Booking does not duplicate Family name, phone, email, or address. APIs may
return Family summary data for read convenience, but that data is read through
the Family reference.

## Reference Entities

`Package` and `PackageAddon` are database-driven reference entities scoped by
organization and branch.

They are not enums because package and addon catalogs need to change without
code deployments.

## Business Rules

- Every Booking belongs to exactly one Family.
- Every Booking is created from a `BOOKED` Opportunity.
- Every Booking contains at least one BookingItem.
- Booking totals are calculated from BookingItems and BookingItemAddons.
- `balance_amount = total_amount - advance_received`.
- A ShootSchedule belongs to one BookingItem.
- PhotographerAssignment belongs to ShootSchedule.
- Cancelled bookings are read-only.
- Family profile fields are not persisted in Booking tables.

## Domain Events

Sprint 4 continues the audit-backed event approach used by Sprints 1-3.

Implemented audit-backed events:

- `BookingCreated`
- `BookingConfirmed`
- `BookingCancelled`
- `BookingCompleted`
- `ShootScheduled`
- `ShootRescheduled`
- `ShootCompleted`
- `PhotographerAssigned`

These are not asynchronous integration events. A durable outbox remains future
technical work.

## RBAC

| Role | Access |
| --- | --- |
| Owner | Full access |
| Branch Manager | Full branch access |
| Sales Executive | Create and view bookings; cannot assign photographers |
| Photographer | View assigned shoots |
| Editor | Read only |
| Customer Success | Read only |

Backend permissions remain authoritative. Frontend role routing only controls UI
navigation.

## Sprint 5 Boundaries

Sprint 5 may build on Booking references for downstream fulfillment work.
Gallery, Editing, Delivery, Payments, WhatsApp, and AI remain outside Sprint 4.
