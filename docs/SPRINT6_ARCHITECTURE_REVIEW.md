# Sprint 6 Architecture Review

Review date: 2026-06-10  
Scope: ALRSCRM after Sprints 1-5, before Sprint 6 implementation.

Reviewed documents:

- `docs/PROJECT_COMPLETION_REPORT.md`
- `docs/DOMAIN_MODEL_REVIEW.md`
- `docs/SPRINT3_ARCHITECTURE_DECISIONS.md`
- `docs/SPRINT4_BOOKING_DOMAIN.md`
- `docs/SPRINT5_GALLERY_DOMAIN.md`
- `docs/GALLERY_AGGREGATE_DIAGRAM.md`
- `docs/GALLERY_EVENT_MAP.md`

Validated against current backend and frontend structure, including Identity,
Family, Sales, Booking, Gallery, RBAC seeds, routes, services, dashboard pages,
and gallery selection code.

## Executive Summary

ALRSCRM has a coherent workflow through client gallery selection:

```text
Lead -> Opportunity -> Booking -> Shoot -> Gallery Upload -> Client Selection -> Selection Submitted
```

The production workflow after selection submission is not implemented. Sprint 6
should introduce Production Management only:

```text
Gallery Selection Submitted -> EditingJob -> EditingTask -> EditingReview -> ReadyForDelivery
```

`EditingJob` must be the aggregate root. Delivery, Payments, AI, and final
client delivery must stay out of Sprint 6.

## Current Aggregates

| Aggregate Or Entity | Current Owner | Sprint 6 Impact |
| --- | --- | --- |
| `Organization` | Identity | Continue as tenant root/reference. |
| `Branch` | Identity | Continue as branch scope reference. |
| `User` | Identity | Editors, reviewers, and managers will reference users. |
| `Family` | Family CRM | Must remain owner of customer profile data. |
| `Opportunity` | Sales | No Sprint 6 ownership change. |
| `FollowUp` | Opportunity child | Not part of Sprint 6. |
| `Booking` | Fulfillment | Editing must reference Booking context but not mutate Booking totals. |
| `BookingItem` | Booking child | Editing should usually start from selected photos for one BookingItem. |
| `ShootSchedule` | Booking child | Can provide production context but should not own editing state. |
| `PhotographerAssignment` | Booking child | Not the editing assignment model. |
| `Package` | Booking reference | Can inform expected deliverables later, but not Sprint 6 workflow owner. |
| `Gallery` | Gallery | Selection source; must not own editing production state. |
| `GalleryPhoto` | Gallery child | Editing input photo reference. |
| `FavoriteSelection` | Gallery child | Client-selected input for EditingJob. |
| `GalleryUpgradeRequest` | Gallery/payment-adjacent reference | Currently exists, but payment ownership is incomplete and must not become Sprint 6 scope. |
| `AuditLog` | Shared audit | Useful for activity timeline, not a domain event outbox. |

## Current APIs

Completed API groups exist for auth, identity, family, sales, bookings,
packages, schedules, assignments, and galleries.

Sprint 6 API gap:

- No `/api/v1/editing-jobs`
- No `/api/v1/editing-tasks`
- No `/api/v1/editing-reviews`
- No production dashboard API
- No editor workload API
- No review queue API
- No ready-for-delivery queue API

Recommended Sprint 6 API shape:

- `GET /api/v1/editing-jobs`
- `POST /api/v1/editing-jobs`
- `GET /api/v1/editing-jobs/{id}`
- `PUT /api/v1/editing-jobs/{id}`
- `POST /api/v1/editing-jobs/{id}/start`
- `POST /api/v1/editing-jobs/{id}/submit-for-review`
- `POST /api/v1/editing-jobs/{id}/approve`
- `POST /api/v1/editing-jobs/{id}/request-changes`
- `POST /api/v1/editing-jobs/{id}/mark-ready-for-delivery`
- `GET /api/v1/editing-jobs/metrics`

All write endpoints must enforce tenant and branch scope through referenced
Gallery, BookingItem, and Booking.

## Current RBAC

Current roles already include `Editor`, but no editing permissions exist.

Current gallery issue:

- `POST /api/v1/galleries/{gallery_id}/reopen-selection` requires
  `galleries:reopen`, but `galleries:reopen` is not present in identity seed
  permissions. This means the route is effectively inaccessible unless a
  permission is manually inserted.

Sprint 6 required permissions:

- `production:editing_jobs:read`
- `production:editing_jobs:write`
- `production:editing_jobs:assign`
- `production:editing_jobs:review`
- `production:editing_jobs:ready_for_delivery`
- `production:editing_tasks:read`
- `production:editing_tasks:write`
- `production:metrics:read`

Recommended role mapping:

| Role | Sprint 6 Access |
| --- | --- |
| Super Admin | Full production access. |
| Owner | Full organization production access. |
| Branch Manager | Full branch production access. |
| Customer Success | Read production status and ready-for-delivery queue. |
| Editor | Assigned editing jobs and tasks only. |
| Photographer | Read production status for own shoot context only, no editing writes. |
| Sales Executive | Read high-level production status only if needed for customer follow-up. |
| Client | No CRM production access. |

## Current Workflows

Implemented:

- Lead and family CRM intake.
- Opportunity pipeline and booking conversion.
- Booking and shoot scheduling.
- Photographer assignment.
- Gallery upload.
- Client favorite selection.
- Selection submission and locking.
- Selection reopen.
- Gallery upgrade request.

Missing workflow after selection submission:

- Create EditingJob from submitted Gallery selection.
- Assign editor.
- Break work into EditingTasks.
- Track editing start, progress, blocked state, and completion.
- Internal review.
- Revision request and rework.
- Approval.
- Mark ready for delivery.

Sprint 6 must not implement:

- Client delivery portal.
- Payment collection.
- AI editing automation.
- Invoice or receipt generation.

## Current Reporting

Current dashboards expose sales and booking metrics. Gallery metrics exist, but
the main dashboard does not yet show production workload.

Missing Sprint 6 reporting:

- Editing jobs pending assignment.
- Editing jobs in progress.
- Editing jobs awaiting review.
- Editing jobs needing changes.
- Jobs ready for delivery.
- Overdue editing jobs.
- Editor workload by user.
- Average editing turnaround time.
- Review rejection rate.
- SLA compliance.

## Current DDD Boundaries

The existing boundary sequence is sound:

```text
Family -> Opportunity -> Booking -> Gallery -> EditingJob -> Delivery
```

Sprint 6 boundary rules:

- `EditingJob` is a new aggregate root.
- `EditingJob` references Gallery, Booking, BookingItem, Family, Organization,
  and Branch by ID.
- `EditingJob` may reference selected GalleryPhoto IDs as source inputs.
- `EditingJob` must not own GalleryPhoto, FavoriteSelection, Family, Booking,
  or Delivery state.
- `EditingTask` is child-owned by EditingJob.
- `EditingReview` is child-owned by EditingJob.
- `ReadyForDelivery` is a terminal production state, not a Delivery aggregate.

## Current Scalability Risks

- No outbox exists; audit rows cannot safely power notifications or automation.
- Production dashboards will need dedicated query patterns, not repeated joins
  over all child rows.
- Gallery selection count is denormalized and manually maintained; Sprint 6
  should avoid relying on stale counters for job creation.
- Large photo sets need pagination or projection APIs for production queues.
- DigitalOcean signed URL generation per photo may become expensive for large
  gallery and editing screens.
- Editor workload views require indexes on branch, assigned editor, status, due
  date, and created timestamp.
- Editing SLAs require reliable server-side timestamps, not frontend state.

## Current Security Risks

- Gallery reopen route uses an unseeded permission code.
- Gallery upgrade request approval/rejection/payment marking should scope
  through the referenced Gallery before mutation; the service currently fetches
  upgrade requests directly by ID.
- Public gallery password authentication contains expiry-check code under an
  unreachable branch after `raise NotFoundError`; expiry protection exists in
  public gallery reads and submit flow, but authentication should still be
  cleaned up before relying on it operationally.
- Public selection endpoints use gallery owner as audit actor; this is useful
  for non-null audit rows but does not identify the client actor.
- Audit rows are not an integration-event security boundary.
- Download permissions and watermark flags exist, but Sprint 6 should avoid
  exposing original production files through public URLs.

## Current Missing Business Requirements

Sprint 6 must clarify or implement:

- Who can create an EditingJob: automatic after selection submission, manual by
  manager, or both.
- Whether one submitted Gallery creates one EditingJob or one job per
  BookingItem.
- Whether all favorites or only submitted favorites are editing inputs.
- How additional purchased selections are handled before production starts.
- Editing due-date rules and SLA targets by service type or package.
- Assignment policy: manual assignment, self-pickup, or workload balancing.
- Review policy: who reviews, how many review rounds, and whether reviewers can
  be editors.
- Blocked reasons and required notes.
- Whether editing output files are stored in Gallery storage or future Delivery
  storage. Recommendation: Sprint 6 tracks output metadata only if needed and
  does not expose delivery.

## Current Technical Debt

- Domain behavior is mostly service-layer procedural logic rather than aggregate
  methods.
- API response envelope remains generic, reducing generated type precision.
- Audit-backed events are not outbox-backed.
- Some gallery service methods commit multiple times for a single logical
  operation.
- Dashboard activity is static in the frontend.
- Current production status is implicit; there is no post-selection source of
  truth.
- The Gallery event map is behind current implementation because it does not
  include selection submission, reopen, password authentication, or upgrade
  request events.

## Current Missing Audit Events

Missing or not yet documented for current Gallery behavior:

- `gallery.selection_submitted`
- `gallery.selection_reopened`
- `gallery.password_authenticated`
- `gallery.upgrade_requested`
- `gallery.upgrade_approved`
- `gallery.upgrade_rejected`
- `gallery.upgrade_paid`

Required Sprint 6 audit-backed events:

- `editing_job.created`
- `editing_job.assigned`
- `editing_job.started`
- `editing_job.submitted_for_review`
- `editing_job.changes_requested`
- `editing_job.approved`
- `editing_job.ready_for_delivery`
- `editing_job.cancelled`
- `editing_task.created`
- `editing_task.completed`
- `editing_review.created`

## Current Missing KPIs

Required Sprint 6 KPIs:

- Total Editing Jobs
- Pending Assignment
- In Progress
- Awaiting Review
- Changes Requested
- Ready For Delivery
- Overdue Jobs
- Average Turnaround Time
- Editor Utilization
- SLA Compliance
- Review Rejection Rate

## Current Missing Dashboards

Required Sprint 6 dashboards:

- Production Overview Dashboard
- Editor Work Queue
- Review Queue
- Ready For Delivery Queue
- Branch Manager Production Dashboard
- Owner Cross-Branch Production Dashboard

## Current Missing Notifications

Sprint 6 should define notification triggers but can keep delivery mechanism as
future work unless the implementation scope explicitly includes notifications.

Missing notification triggers:

- Selection submitted and ready for production.
- Editing job assigned.
- Editing due date approaching.
- Editing job overdue.
- Review requested.
- Changes requested.
- Editing approved.
- Ready for delivery.

## Current Missing Automation

Recommended automations:

- Auto-create EditingJob when Gallery selection is submitted.
- Auto-calculate due date from service type/package SLA.
- Auto-mark overdue jobs by server-side scheduled job.
- Auto-surface workload warnings before assigning overloaded editors.
- Auto-create review task when editing is submitted.

Do not implement automation using read-time mutation. Use explicit commands,
transactional service methods, or a future scheduled worker.

## Sprint 6 Architecture Decision

Sprint 6 should introduce a new `production` or `editing` bounded context with
`EditingJob` as the aggregate root.

The handoff event is Gallery selection submission. EditingJob should reference
Gallery and selected photos, then own all production workflow state until the
job reaches `READY_FOR_DELIVERY`.

Delivery remains a future aggregate and should only consume ready production
state later.
