# Sprint 6 Editing Domain

Sprint 6 introduces Production Management for editing workflow only.

It does not implement:

- Final delivery
- Payments
- Invoices
- WhatsApp
- AI
- Client download delivery

## Domain Goal

After a client submits gallery selections, the studio needs an operational
system to assign editing work, track production progress, review output, request
changes, and mark work ready for a future delivery workflow.

Sprint 6 fills this gap:

```text
Gallery Selection Submitted
  -> EditingJob
  -> EditingReview
  -> ReadyForDelivery
```

## Explicit Architecture Rejection

Sprint 6 must not create one EditingTask row per selected photo.

Reason:

- High row count
- Little business value
- Operational complexity

Production progress is tracked with `selected_photo_count` and
`completed_photo_count` on `EditingJob`.

## Aggregate Boundary

`EditingJob` is the aggregate root.

`EditingJob` references:

- `organization_id`
- `branch_id`
- `booking_id`
- `booking_item_id`
- `gallery_id`
- `assigned_editor_id`

`EditingJob` owns:

- Priority
- Editing status
- Selected photo count
- Completed photo count
- Due date
- Start and completion timestamps
- Internal notes
- `EditingReview` child collection

`EditingJob` must not own:

- Family profile data
- Booking totals
- Package pricing
- Gallery access rules
- Gallery photos as storage objects
- Final delivery state
- Payment state

## Entity Ownership

### EditingJob

Root entity for production tracking.

Responsibilities:

- Validate that source Gallery is selection-submitted.
- Own editor assignment.
- Own production status transitions.
- Own progress counts.
- Own review state.
- Expose production KPIs.

### EditingReview

Child entity of EditingJob.

Responsibilities:

- Capture reviewer decision.
- Capture approval or rejection notes.
- Capture reviewer and reviewed timestamp.
- Preserve review history.

`EditingReview` has no independent lifecycle outside EditingJob.

### ReadyForDelivery

`ReadyForDelivery` is a state of `EditingJob`, not a separate Sprint 6
aggregate.

Future Delivery may later create its own aggregate from an EditingJob in
`READY_FOR_DELIVERY` state.

## Relationships

```text
Family
  <- Booking
      <- BookingItem
          <- Gallery
              <- FavoriteSelection / GalleryPhoto
                  -> EditingJob
                      -> EditingReview
                      -> READY_FOR_DELIVERY state
```

Relationship rules:

- Every EditingJob belongs to exactly one Gallery.
- Every EditingJob belongs to exactly one BookingItem.
- Every EditingJob belongs to exactly one Booking.
- One Gallery has one EditingJob in Sprint 6.
- EditingJob stores selected and completed counts, not one row per photo.
- EditingJob does not duplicate customer name, phone, email, or address.

## Status Flow

`EditingStatus` values:

- `PENDING`
- `ASSIGNED`
- `IN_PROGRESS`
- `READY_FOR_REVIEW`
- `APPROVED`
- `REJECTED`
- `READY_FOR_DELIVERY`

Allowed transitions:

```text
PENDING -> ASSIGNED
ASSIGNED -> IN_PROGRESS
IN_PROGRESS -> READY_FOR_REVIEW
READY_FOR_REVIEW -> APPROVED
READY_FOR_REVIEW -> REJECTED
REJECTED -> IN_PROGRESS
APPROVED -> READY_FOR_DELIVERY
```

Invalid transitions:

- Direct `PENDING` to `READY_FOR_REVIEW`.
- Direct `PENDING` to `READY_FOR_DELIVERY`.
- Direct `IN_PROGRESS` to `READY_FOR_DELIVERY`.
- Any mutation after `READY_FOR_DELIVERY` without a future administrative
  reopen policy.

## Priority And Due Date Rules

`EditingPriority` values:

- `LOW`
- `NORMAL`
- `HIGH`
- `URGENT`

Due date is calculated from `selection_submitted_at`:

| Priority | Due Date |
| --- | --- |
| `LOW` | `selection_submitted_at + 10 days` |
| `NORMAL` | `selection_submitted_at + 7 days` |
| `HIGH` | `selection_submitted_at + 3 days` |
| `URGENT` | `selection_submitted_at + 1 day` |

Managers may override due date.

## Business Rules

- EditingJob is auto-created when Gallery becomes `SELECTION_SUBMITTED`.
- Manual EditingJob creation is allowed only for a submitted Gallery.
- `selected_photo_count` is the count of selected favorites at job creation.
- `completed_photo_count` starts at `0`.
- Default status is `PENDING`.
- Default priority is `NORMAL`.
- Cannot assign editor if status is `READY_FOR_DELIVERY`.
- Cannot move to `READY_FOR_REVIEW` unless
  `completed_photo_count = selected_photo_count`.
- Cannot move to `READY_FOR_DELIVERY` unless review is approved.
- Editor cannot approve or reject their own assigned job.
- Editor can update assigned work but cannot approve.
- Branch and tenant scope must be enforced through EditingJob columns, not joins
  alone.

## Booking Integration

Booking remains the fulfillment aggregate.

EditingJob references:

- `booking_id`
- `booking_item_id`

EditingJob reads but does not own:

- Booking number
- Service type
- Package context
- Shoot schedule context

Booking should not persist editing status. Booking-level production status
should be a projection from EditingJob.

## Gallery Integration

Gallery remains the selection aggregate.

EditingJob is created from:

- Gallery in `SELECTION_SUBMITTED` state
- Current selected favorite count

Gallery should not own:

- Editor assignment
- Editing status
- Review status
- Ready-for-delivery state

Gallery may expose whether an EditingJob exists as read-only derived data in a
future projection.

## Delivery Integration

Delivery is future scope.

Future Delivery should be created from:

- EditingJob in `READY_FOR_DELIVERY` state

Delivery should own:

- Client delivery package
- Delivery access links
- Download expiry
- Final delivered file state
- Delivery notification state

## Payment Integration

Payments remain future scope.

EditingJob should not own:

- Payment status
- Upgrade payment collection
- Invoice or receipt state
- Gateway transaction metadata

If future paid upgrades affect selected photo count, Sprint 6 should consume
approved and paid selection state without implementing the payment aggregate.

## Future Sprint Compatibility

Sprint 6 preserves these future integrations:

- Delivery can consume `READY_FOR_DELIVERY` jobs.
- Payments can charge for delivery, upgrades, or outstanding balances without
  changing EditingJob ownership.
- AI can later attach automation metadata to EditingJob without becoming the
  aggregate owner.
- Notifications can subscribe to audit-backed events initially and a future
  outbox later.
- Reporting can use EditingJob timestamps and review rows for SLA metrics.

## Required KPIs

Sprint 6 exposes:

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

## Required Dashboards

Sprint 6 provides:

- Production Dashboard
- Editing Queue
- Editing Job Detail
- Editor Dashboard

Owner, Organization Admin, and Branch Manager dashboards are scoped by tenant
and branch. Editor dashboards show assigned work only.
