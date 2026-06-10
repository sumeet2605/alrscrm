# Editing Event Map

ALRSCRM currently records domain events as audit rows. Sprint 6 continues that
convention and does not introduce an outbox, message bus, Kafka, RabbitMQ,
Celery, or NATS.

These events are audit-backed domain events, not asynchronous integration
events.

## Upstream Events

| Upstream Owner | Event | Sprint 6 Use |
| --- | --- | --- |
| Gallery | `gallery.selection_submitted` | Creates EditingJob in the same transaction. |
| Gallery | `gallery.selection_reopened` | Future policy may block reopen after editing starts. |
| Gallery | `gallery.upgrade_paid` | Future policy may affect selected count before production starts. |

## Editing Events

| Audit Event | Domain Event | Owner | Trigger |
| --- | --- | --- | --- |
| `editing.job_created` | `EditingJobCreated` | EditingJob | Job created from submitted Gallery. |
| `editing.editor_assigned` | `EditingEditorAssigned` | EditingJob | Editor assigned or reassigned. |
| `editing.started` | `EditingStarted` | EditingJob | Editor starts production work. |
| `editing.review_submitted` | `EditingReviewSubmitted` | EditingJob | Completed work submitted for review. |
| `editing.approved` | `EditingApproved` | EditingJob | Reviewer approves work. |
| `editing.rejected` | `EditingRejected` | EditingJob | Reviewer rejects work. |
| `editing.ready_for_delivery` | `EditingReadyForDelivery` | EditingJob | Approved work marked ready for future delivery. |

## Event Ownership

Editing owns:

- Editor assignment events
- Production progress events
- Review result events
- Ready-for-delivery event

Gallery owns:

- Photo upload events
- Favorite selection events
- Selection submission and reopen events

Booking owns:

- Booking creation and scheduling events
- Shoot completion events

Delivery will own future:

- Delivery created
- Delivery published
- Delivery viewed
- Delivery downloaded
- Delivery completed

Payment will own future:

- Invoice created
- Payment requested
- Payment received
- Refund issued

## Required Event Metadata

Every Sprint 6 audit event should include:

- `organization_id`
- `branch_id`
- `editing_job_id`
- `gallery_id`
- `booking_id`
- `booking_item_id`
- `actor_user_id`
- `domain_event`

Assignment and review events should also include:

- `assigned_editor_id` where applicable
- Reviewer user ID where applicable
- Previous status when practical
- New status when practical

## Workflow Event Sequence

```text
gallery.selection_submitted
  -> editing.job_created
  -> editing.editor_assigned
  -> editing.started
  -> editing.review_submitted
  -> editing.approved
  -> editing.ready_for_delivery
```

Revision loop:

```text
editing.review_submitted
  -> editing.rejected
  -> editing.started
  -> editing.review_submitted
```

## Missing Infrastructure

The project still lacks:

- Domain event outbox
- Message bus
- Retryable event handlers
- Notification dispatcher
- SLA scheduler

Until those exist, Sprint 6 events are recorded transactionally as audit rows
and used only for internal history/reporting.
