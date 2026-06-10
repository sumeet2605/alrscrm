# Sprint 7 Architecture Review

Sprint 7 introduces Delivery Management after Sprint 6 Production Management.

This review was completed before implementation and validates Sprint 7 against:

- `docs/PROJECT_COMPLETION_REPORT.md`
- `docs/DOMAIN_MODEL_REVIEW.md`
- `docs/SPRINT4_BOOKING_DOMAIN.md`
- `docs/SPRINT5_GALLERY_DOMAIN.md`
- `docs/SPRINT6_EDITING_DOMAIN.md`
- `docs/EDITING_AGGREGATE_DIAGRAM.md`
- `docs/EDITING_EVENT_MAP.md`
- `docs/SPRINT6_FINAL_SIGNOFF.md`
- Current Booking, Gallery, Editing, and frontend implementation

No Sprint 7 implementation has been started in this review document.

## Executive Decision

Delivery should be its own aggregate root.

`DeliveryJob` belongs in a separate Delivery bounded context because it owns a
new lifecycle after editing is complete:

```text
EditingJob READY_FOR_DELIVERY
  -> DeliveryJob
  -> zip generation
  -> client delivery
  -> downloads
  -> expiry
  -> reopen request
  -> reopened or closed
```

Delivery must not be modeled as a field on `EditingJob`, `Gallery`, or
`Booking`. Those aggregates are already correctly scoped:

- `Booking` owns fulfillment order structure, booking items, schedules, and
  photographer assignments.
- `Gallery` owns photo storage metadata, public selection access, favorites,
  and selection submission.
- `EditingJob` owns production editing workflow, assignment, progress, reviews,
  approval, and `READY_FOR_DELIVERY` readiness.
- `DeliveryJob` should own final client delivery, download policy, delivery
  audit, expiry, and reopen workflow.

## 1. Delivery Aggregate Boundary

`DeliveryJob` should be the Sprint 7 aggregate root.

`DeliveryJob` references:

- `organization_id`
- `branch_id`
- `family_id`
- `booking_id`
- `gallery_id`
- `editing_job_id`

`DeliveryJob` owns:

- `delivery_number`
- `delivery_status`
- `edited_photo_count`
- `delivery_date`
- `expiry_date`
- `delivery_link`
- `download_count`
- `max_downloads`
- `allow_re_download`
- `re_download_fee`
- `watermark_enabled`
- `original_download_enabled`
- `zip_generation_status`
- `client_notified_at`
- `last_downloaded_at`
- `delivery_notes`
- `deleted_at`
- `DeliveryDownload` child records
- `DeliveryAudit` child records

Required uniqueness:

```text
unique(gallery_id)
unique(editing_job_id)
unique(delivery_number)
```

The `unique(gallery_id)` rule preserves the requested one DeliveryJob per
Gallery invariant. `unique(editing_job_id)` prevents duplicate delivery jobs if
the ready-for-delivery workflow is retried.

## 2. What Delivery Should Own

Delivery should own only final delivery lifecycle and access policy:

- Delivery readiness after editing handoff.
- ZIP generation state.
- Delivery link generation and publication.
- Client sent/delivered status.
- Expiry enforcement.
- Download limits.
- Download history.
- Re-download request and approval workflow.
- Delivery-specific audit trail.
- Delivery dashboard metrics.

Delivery should not own:

- Original or edited photo storage metadata.
- Gallery favorites.
- Selection limits.
- Editing progress or review decisions.
- Booking package pricing.
- Payment settlement.
- Family customer profile fields.

## 3. What Remains Owned By Gallery

Gallery remains the selection and photo-access aggregate.

Gallery continues to own:

- `Gallery`
- `GalleryPhoto`
- `FavoriteSelection`
- `GalleryUpgradeRequest`
- Photo storage paths and thumbnails.
- Gallery password and selection access rules.
- Gallery expiry for selection access.
- Favorite selection count and locking.
- Selection submission and reopen behavior.

Delivery may read Gallery information to determine source content and public
context, but Delivery must not mutate Gallery selection state or duplicate photo
storage metadata.

## 4. What Remains Owned By EditingJob

EditingJob remains the production aggregate.

EditingJob continues to own:

- Editor assignment.
- Editing priority.
- Editing status transitions.
- Selected photo count captured at production start.
- Completed photo count.
- Review submission.
- Approval and rejection.
- `READY_FOR_DELIVERY` readiness.
- `EditingReview` child records.

Sprint 7 should add only one side effect to the approved Sprint 6 lifecycle:
when an EditingJob transitions to `READY_FOR_DELIVERY`, a DeliveryJob is created
idempotently.

EditingJob must remain read-only after `READY_FOR_DELIVERY`. Delivery owns the
delivery lifecycle from that point forward.

## 5. Future Payment Integration Strategy

Payments are not implemented in Sprint 7.

Future Payment should reference `delivery_job_id` when collecting money for:

- Re-download fees.
- Extra edited photo requests.
- Extra delivery requests.

Sprint 7 may store `re_download_fee` for business policy and reporting, but it
must not store payment status, transaction references, invoices, GST data, or
gateway metadata.

Future Payment should reference:

- `organization_id`
- `branch_id`
- `family_id`
- `booking_id`
- `delivery_job_id`

Payment may render Family details for invoices in a later sprint, but customer
profile data must continue to come from Family unless a later accounting
requirement explicitly introduces immutable legal billing snapshots.

## 6. Future WhatsApp Automation Strategy

WhatsApp is not implemented in Sprint 7.

Sprint 7 should prepare for notification automation by recording:

- `client_notified_at`
- delivery audit event metadata
- delivery status transitions

Future WhatsApp automation should consume delivery events through an outbox or
notification dispatcher. Until that infrastructure exists, Sprint 7 events
remain audit-backed domain events only and must not be treated as retryable
integration events.

Delivery should not directly depend on WhatsApp provider APIs in Sprint 7.

## 7. Audit-Backed Events Required

ALRSCRM currently records domain events as audit rows. Sprint 7 should continue
that convention and must not introduce an event bus or outbox.

Required audit-backed delivery events:

| Audit Event | Domain Event | Owner | Trigger |
| --- | --- | --- | --- |
| `delivery.job_created` | `DeliveryJobCreated` | DeliveryJob | EditingJob reaches `READY_FOR_DELIVERY` or manual creation succeeds. |
| `delivery.zip_generated` | `DeliveryZipGenerated` | DeliveryJob | ZIP generation completes. |
| `delivery.sent` | `DeliverySent` | DeliveryJob | Delivery link is sent to client. |
| `delivery.downloaded` | `DeliveryDownloaded` | DeliveryJob | Client download succeeds. |
| `delivery.expired` | `DeliveryExpired` | DeliveryJob | Delivery becomes expired. |
| `delivery.reopen_requested` | `DeliveryReopenRequested` | DeliveryJob | Client requests re-download or reopen. |
| `delivery.reopened` | `DeliveryReopened` | DeliveryJob | Manager approves reopen. |
| `delivery.closed` | `DeliveryClosed` | DeliveryJob | Delivery lifecycle is closed. |

Each event should include:

- `organization_id`
- `branch_id`
- `delivery_job_id`
- `family_id`
- `booking_id`
- `gallery_id`
- `editing_job_id`
- `actor_user_id` when authenticated
- `domain_event`

Download events should also include:

- IP address
- user agent
- download count after increment

## 8. KPI Requirements

Sprint 7 should introduce delivery dashboard metrics:

- Pending Delivery
- Ready Delivery
- Delivered
- Expired
- Reopened
- Average Delivery TAT
- Downloads This Month
- Re-download Revenue Potential

Recommended definitions:

```text
Pending Delivery = count(status = PENDING)
Ready Delivery = count(status = READY)
Delivered = count(status = DELIVERED)
Expired = count(status = EXPIRED)
Reopened = count(status in REOPEN_REQUESTED, REOPENED)
Average Delivery TAT = average(delivery_date - editing_job.completed_at)
Downloads This Month = count(DeliveryDownload.downloaded_at in current month)
Re-download Revenue Potential = count(REOPEN_REQUESTED) * re_download_fee
```

Metric queries must enforce organization and branch scope through DeliveryJob
columns.

## 9. RBAC Permissions Required

Sprint 7 should seed these permissions:

- `delivery:view`
- `delivery:create`
- `delivery:update`
- `delivery:send`
- `delivery:reopen`
- `delivery:download_audit`
- `delivery:dashboard`

Recommended role assignment:

| Role | Access |
| --- | --- |
| Super Admin | All delivery permissions. |
| Organization Admin | All delivery permissions within organization scope. |
| Owner | All delivery permissions for backward compatibility. |
| Branch Manager | All delivery permissions within branch scope. |
| Editor | `delivery:view` only. |
| Photographer | No delivery permissions by default. |
| Sales Executive | No delivery permissions by default. |
| Customer Success | `delivery:view` and `delivery:dashboard` only if support workflows require it; otherwise no default access. |

The client delivery page is public-client access and should not use staff RBAC.
It must instead enforce DeliveryJob expiry, download limits, and link validity.

## 10. Production Risks

### Public Link Security

The requested route `/client/delivery/{deliveryId}` exposes a UUID-based public
identifier. UUIDs are difficult to guess but still not a complete access model
for sensitive family photos.

Sprint 7 should at minimum enforce:

- DeliveryJob existence.
- Delivery status.
- Expiry.
- Download limit.

Recommended future hardening:

- Signed delivery token.
- Optional delivery password.
- Short-lived signed storage URLs.
- Rate limiting.
- Audit trail for failed download attempts.

### Large ZIP Generation

ZIP generation can be mocked or stubbed in Sprint 7, but production ZIP
generation can become memory and CPU intensive.

Future production implementation should use:

- Background worker.
- Streaming ZIP creation.
- Object storage output.
- Retry metadata.
- Failure audit events.

### Read-Time Expiry Mutation

Automatically changing `READY` or `SENT` deliveries to `EXPIRED` during a read
can create hidden write side effects similar to the Sprint 3 follow-up aging
risk.

Preferred approach:

- Explicit service method with tenant and branch scope.
- Scheduled job in a future worker.
- If read-time expiry is used temporarily, scope it by DeliveryJob and record
  `delivery.expired`.

### Download Race Conditions

Concurrent downloads can exceed `max_downloads` if increments are not atomic.

Recommended persistence behavior:

- Lock the DeliveryJob row before incrementing download count.
- Record `DeliveryDownload` and increment count in the same transaction.
- Re-check expiry and max downloads inside the transaction.

### Storage Provider Coupling

Gallery storage currently supports local and DigitalOcean-compatible object
storage. Delivery should not copy GalleryPhoto storage paths into DeliveryJob.
It should read source photos from Gallery and generate delivery artifacts
through the existing storage provider abstraction.

### Audit Is Not Integration Infrastructure

Delivery events are audit-backed only. They are suitable for internal history
and reports, but not for reliable WhatsApp, email, payment, or automation
workflows until an outbox exists.

### Family Data Duplication

Delivery references `family_id` for reporting and client context. It must not
persist duplicated Family name, phone, email, or address.

## Required Implementation Guardrails

- Do not change Booking ownership.
- Do not change Gallery ownership.
- Do not change EditingJob workflow semantics.
- Do not create DeliveryJob before `READY_FOR_DELIVERY`.
- Create DeliveryJob idempotently when EditingJob becomes
  `READY_FOR_DELIVERY`.
- Enforce one DeliveryJob per Gallery.
- Enforce organization and branch scope on all staff delivery APIs.
- Keep public client delivery access separate from staff RBAC.
- Keep Payment, Invoice, WhatsApp, Email, AI, and outbox/event-bus out of
  Sprint 7.

## Architecture Verdict

Sprint 7 should proceed with `DeliveryJob` as a new aggregate root in a Delivery
bounded context.

This preserves the existing Sprint 4, Sprint 5, and Sprint 6 aggregate
boundaries while adding the next operational lifecycle after editing approval.
The implementation should be intentionally narrow: delivery lifecycle, download
policy, download audit, reopen workflow, dashboard metrics, staff UI, and public
client delivery view.
