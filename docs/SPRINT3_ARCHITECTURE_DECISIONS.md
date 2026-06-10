# Sprint 3 Architecture Decisions

## Review Basis

This document was generated before Sprint 3 implementation and validates Sprint
3 boundaries against:

- `docs/Family_Aggregate_Diagram.md`
- `docs/Domain_Event_Map.md`
- `docs/DOMAIN_MODEL_REVIEW.md`
- `docs/SPRINT2_COMPLETION_REPORT.md`

Sprint 3 must preserve the Sprint 2 Family aggregate boundary. It adds the
sales pipeline around Family references; it does not move customer profile data
into sales tables.

## Decision 1: Opportunity Aggregate Boundary

`Opportunity` is the Sales Pipeline aggregate root.

`Opportunity` references:

- `organization_id`
- `branch_id`
- `family_id`
- `assigned_to_user_id`
- `lost_reason_id`

`Opportunity` owns:

- Current pipeline stage
- Estimated value
- Probability
- Expected booking date
- Opportunity-level notes
- Soft-delete state
- Follow-up child collection
- Opportunity note child collection

`Opportunity` must not own or duplicate customer profile fields from `Family`.
Do not copy these fields into Opportunity:

- Name
- Phone
- Email
- Address
- Family member details

The UI and APIs may return Family summary data for read convenience, but that
summary must be read from the Family aggregate and not persisted as duplicate
Opportunity state.

## Decision 2: FollowUp Aggregate Boundary

`FollowUp` is a child entity of `Opportunity`, not a separate aggregate root.

Reasoning:

- A follow-up has no useful lifecycle without an Opportunity.
- A follow-up must be assigned to a user and have a due date.
- Follow-up status contributes to Opportunity pipeline execution and dashboard
  KPIs.

Sprint 3 APIs may expose `/api/v1/followups` for workflow convenience, but
service logic must still enforce Opportunity ownership, tenant scope, and branch
scope through the parent Opportunity.

Allowed `FollowUpStatus` values:

- `PENDING`
- `COMPLETED`
- `MISSED`

Dashboard visibility:

- Missed follow-ups must be queryable for dashboard display.
- Follow-up compliance must be visible on dashboards.

## Decision 3: LostReason Ownership

`LostReason` is a separate database-driven reference entity.

It must not be an enum because business users need reporting and future
administration over loss reasons without code changes.

Initial seed values:

- Too Expensive
- Need Spouse Approval
- Comparing Competitors
- Not Ready Yet
- Stopped Responding

Ownership rules:

- `LostReason` is owned by the Sales bounded context.
- `Opportunity` references `lost_reason_id`.
- `lost_reason_id` is mandatory when an Opportunity stage becomes `LOST`.
- Sales users must not delete lost reasons.
- Sprint 3 only requires read access through `GET /api/v1/lost-reasons`.

## Decision 4: Future Booking Integration Strategy

Bookings are not implemented in Sprint 3.

Sprint 3 `BOOKED` means the sales Opportunity converted. It does not create a
Booking aggregate yet.

Sprint 4 should introduce a Booking aggregate that references:

- `family_id`
- `opportunity_id`
- `organization_id`
- `branch_id`

Booking creation should be driven from a booked Opportunity, but the Booking
aggregate should own booking-specific scheduling, package, and fulfillment
state. Opportunity should remain the sales conversion record.

When Opportunity stage becomes `BOOKED`:

- Opportunity becomes read-only except for future explicitly allowed audit or
  administrative corrections.
- No customer profile data is copied into Booking when Booking is later added.
- Booking reads customer profile data through `family_id`.

## Decision 5: Future Gallery Integration Strategy

Gallery is not implemented in Sprint 3.

Future Gallery modules must reference `family_id` and, where relevant, the
future `booking_id`.

Gallery must not duplicate:

- Family name
- Phone
- Email
- Address

Gallery should own gallery-specific state only, such as image collections,
selection state, access links, expiry rules, and delivery status.

## Decision 6: Future Payment Integration Strategy

Payments are not implemented in Sprint 3.

Future Payment modules should reference the future Booking aggregate and keep
`family_id` available for reporting and customer-facing context.

Payment must not duplicate Family contact data. Invoice or receipt rendering may
read Family data at render time or store immutable legal billing snapshots only
if a later payment/accounting requirement explicitly needs that. Sprint 3 does
not introduce that requirement.

Payment should own payment-specific state only, such as:

- Amounts
- Payment status
- Transaction references
- Refunds
- Due dates
- Gateway metadata

## Decision 7: Family And Opportunity Relationship Rules

Family remains the aggregate root for customer profile data.

Opportunity relationship rules:

- Every Opportunity belongs to exactly one Family.
- One Family may have multiple Opportunities.
- Opportunity references Family using `family_id`.
- Opportunity must not store customer name, phone, or email.
- Opportunity organization and branch must remain consistent with the referenced
  Family.
- Future modules must reference Family for customer identity and contact data.

Supported future examples for multiple Opportunities on one Family:

- Maternity
- Newborn
- Milestone

## KPI Framework

Sprint 3 must introduce dashboard-ready KPI calculations for the sales pipeline.

Required metrics:

- Conversion Rate
- Booked Opportunities
- Lost Opportunities
- Follow Up Compliance
- Average Opportunity Value

### Conversion Rate

Formula:

```text
Booked Opportunities / Total Opportunities
```

Interpretation:

- Measures sales conversion from tracked Opportunities.
- `BOOKED` is the conversion marker in Sprint 3.

### Booked Opportunities

Formula:

```text
count(Opportunities where current_stage = BOOKED)
```

### Lost Opportunities

Formula:

```text
count(Opportunities where current_stage = LOST)
```

### Follow Up Compliance

Formula:

```text
Completed Follow Ups / Total Due Follow Ups
```

Target:

```text
100%
```

Definition:

- Completed Follow Ups: follow-ups with `status = COMPLETED`.
- Total Due Follow Ups: follow-ups with `due_date` on or before the reporting
  cutoff.

Dashboard rule:

- Follow Up Compliance must be visible on dashboards.
- Missed follow-ups must also be visible on dashboards.

### Average Opportunity Value

Formula:

```text
sum(estimated_value) / count(Opportunities)
```

Scope should follow the caller's RBAC and branch scope.

## Domain Events To Document In Sprint 3

Sprint 2 currently writes audit events only. Sprint 3 may document the following
sales domain event vocabulary, but implementation should remain honest about
whether these are audit rows or true outbox events:

- `OpportunityCreated`
- `OpportunityStageChanged`
- `OpportunityBooked`
- `OpportunityLost`
- `FollowUpCreated`
- `FollowUpCompleted`
- `FollowUpMissed`

If no outbox is implemented in Sprint 3, these must be recorded as audit events
and documented as audit-backed domain events, not as asynchronous integration
events.

## Non-Goals For Sprint 3

- Booking aggregate implementation.
- Gallery aggregate implementation.
- Payment aggregate implementation.
- Duplicating Family profile data into Sales tables.
- Managing lost reasons beyond read access and seed data.
- Creating child-resource APIs that bypass Opportunity ownership rules.
