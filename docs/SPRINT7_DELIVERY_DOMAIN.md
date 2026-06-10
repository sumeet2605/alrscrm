# Sprint 7 Delivery Domain

Sprint 7 introduces Delivery Management after editing is marked ready for
delivery.

It does not implement:

- Payments
- Invoices
- GST
- WhatsApp
- Email
- AI
- Event bus or outbox

## Domain Goal

Delivery starts when an EditingJob reaches `READY_FOR_DELIVERY` and ends when
the client delivery is downloaded, expired, reopened, or closed.

```text
EditingJob READY_FOR_DELIVERY
  -> DeliveryJob
  -> ZIP generated
  -> sent to client
  -> downloaded or expired
  -> optional reopen request
```

## Aggregate Boundary

`DeliveryJob` is the aggregate root.

`DeliveryJob` references:

- `organization_id`
- `branch_id`
- `family_id`
- `booking_id`
- `gallery_id`
- `editing_job_id`

`DeliveryJob` owns:

- Delivery status
- Delivery number
- Edited photo count
- Delivery and expiry dates
- Delivery link
- Download limits and counters
- Re-download policy
- Watermark and original-download policy
- ZIP generation status
- Client notification timestamp
- Delivery notes
- `DeliveryDownload`
- `DeliveryAudit`

## Boundary Rules

- Booking remains the fulfillment aggregate.
- Gallery remains the photo and selection aggregate.
- EditingJob remains the production workflow aggregate.
- DeliveryJob owns only final client delivery lifecycle.
- DeliveryJob does not duplicate Family name, phone, email, or address.
- One Gallery can have only one DeliveryJob.
- One EditingJob can have only one DeliveryJob.

## Status Flow

Delivery statuses:

- `PENDING`
- `ZIP_GENERATING`
- `READY`
- `SENT`
- `DELIVERED`
- `EXPIRED`
- `REOPEN_REQUESTED`
- `REOPENED`
- `CLOSED`

ZIP statuses:

- `PENDING`
- `GENERATING`
- `COMPLETED`
- `FAILED`

## Business Rules Implemented

- EditingJob `APPROVED` does not create a DeliveryJob.
- EditingJob `READY_FOR_DELIVERY` creates a DeliveryJob idempotently.
- Manual DeliveryJob creation requires an EditingJob already in
  `READY_FOR_DELIVERY`.
- Default `max_downloads` is `10`.
- Default `allow_re_download` is `false`.
- Default `re_download_fee` is `0`.
- Default `expiry_date` is `delivery_date + 90 days`.
- Download tracking increments `download_count`.
- Download tracking creates `DeliveryDownload`.
- Downloads stop when `download_count >= max_downloads`.
- Expired public delivery links return `410 Gone`.
- Client reopen requests move delivery to `REOPEN_REQUESTED`.
- Manager reopen approval moves delivery to `REOPENED` and extends expiry.

## Future Payment Integration

Payments remain future scope.

Future Payment should reference `delivery_job_id` for:

- Re-download fees
- Extra edited photos
- Extra delivery requests

Sprint 7 stores only delivery policy values. It does not store payment status,
transaction IDs, invoice data, or tax data.

## Future WhatsApp Integration

WhatsApp remains future scope.

Sprint 7 captures `client_notified_at` and audit-backed delivery events so a
future notification dispatcher can use them. Audit rows are not integration
events until an outbox exists.

