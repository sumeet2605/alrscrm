# Sprint 3 Opportunity Domain

## Purpose

Sprint 3 adds the Sales Pipeline Foundation. The goal is to track opportunities,
follow-ups, stage movement, booked conversions, and lost reasons without
duplicating Family profile data.

## Aggregate Boundary

`Opportunity` is the Sales aggregate root.

Owned child entities:

- `FollowUp`
- `OpportunityNote`
- `OpportunityStageHistory`

Referenced entities:

- `Family`
- `Organization`
- `Branch`
- `User`
- `LostReason`

`LostReason` is a Sales reference entity. It is database-driven, not an enum.

## Family Relationship

Family remains the aggregate root for customer profile data.

Rules:

- Every Opportunity references one Family through `family_id`.
- One Family can have multiple Opportunities.
- Opportunity never stores customer name, phone, email, or address.
- Opportunity organization and branch must match the referenced Family.

## Business Rules

- Every Opportunity must have a stage.
- `LOST` requires `lost_reason_id`.
- `BOOKED` opportunities are read-only.
- Every FollowUp requires `assigned_to_user_id` and `due_date`.
- Overdue pending follow-ups are marked `MISSED` when follow-up lists or metrics are queried.
- Every stage change creates an `OpportunityStageHistory` record.

## Audit-Backed Domain Events

Sprint 3 records domain events as audit rows:

- `OpportunityCreated`
- `OpportunityStageChanged`
- `OpportunityBooked`
- `OpportunityLost`
- `FollowUpCreated`
- `FollowUpCompleted`
- `FollowUpMissed`

There is no asynchronous outbox in Sprint 3.
