# Delivery Event Map

ALRSCRM currently records domain events as audit rows. Sprint 7 continues that
convention and does not add an outbox, queue, or event bus.

These events are audit-backed domain events, not asynchronous integration
events.

## Upstream Events

| Upstream Owner | Event | Sprint 7 Use |
| --- | --- | --- |
| EditingJob | `editing.ready_for_delivery` | Creates DeliveryJob in the same transaction. |

## Delivery Events

| Audit Event | Domain Event | Owner | Trigger |
| --- | --- | --- | --- |
| `delivery.job_created` | `DeliveryJobCreated` | DeliveryJob | DeliveryJob created from ready EditingJob. |
| `delivery.zip_generated` | `DeliveryZipGenerated` | DeliveryJob | ZIP generation completes. |
| `delivery.sent` | `DeliverySent` | DeliveryJob | Client delivery link is sent. |
| `delivery.downloaded` | `DeliveryDownloaded` | DeliveryJob | Client download succeeds. |
| `delivery.expired` | `DeliveryExpired` | DeliveryJob | Delivery passes expiry date. |
| `delivery.reopen_requested` | `DeliveryReopenRequested` | DeliveryJob | Client requests reopen. |
| `delivery.reopened` | `DeliveryReopened` | DeliveryJob | Manager approves reopen. |
| `delivery.closed` | `DeliveryClosed` | DeliveryJob | Delivery is closed. |

## Event Ownership

Delivery owns:

- Delivery creation events
- ZIP generation events
- Send events
- Download events
- Expiry events
- Reopen request and approval events
- Close events

Gallery owns:

- Photo upload events
- Selection events
- Gallery reopen events

Editing owns:

- Editing assignment
- Editing production progress
- Review and approval
- Ready-for-delivery state

Payment will own future:

- Payment requested
- Payment received
- Refund issued
- Invoice created

WhatsApp will own future:

- Message queued
- Message sent
- Message failed
- Message delivered

## Missing Infrastructure

The project still lacks:

- Outbox
- Message bus
- Background ZIP worker
- Notification dispatcher
- Retryable automation handlers

Until those exist, delivery events are transactionally written audit records.

