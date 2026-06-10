# Sprint 3 Database Design

## Migration

Sprint 3 adds:

- `backend/alembic/versions/202606100005_create_sales_pipeline.py`

## Tables

### opportunities

Sales aggregate root.

Key fields:

- `organization_id`
- `branch_id`
- `family_id`
- `assigned_to_user_id`
- `opportunity_type`
- `current_stage`
- `estimated_value`
- `probability`
- `expected_booking_date`
- `lost_reason_id`
- `notes`
- `deleted_at`

Indexes:

- `family_id`
- `assigned_to_user_id`
- `current_stage`
- `opportunity_type`
- `expected_booking_date`
- `created_at`

### followups

Opportunity-owned child entity for sales follow-up work.

Indexes:

- `assigned_to_user_id`
- `status`
- `due_date`

### opportunity_notes

Opportunity-owned notes.

### opportunity_stage_history

Records every stage change.

Indexes:

- `opportunity_id`
- `created_at`

### lost_reasons

Database-driven reference entity seeded with:

- Too Expensive
- Need Spouse Approval
- Comparing Competitors
- Not Ready Yet
- Stopped Responding

## Integrity Notes

- Opportunities reference Families rather than duplicating Family contact data.
- Composite branch/organization foreign key keeps Opportunity branch scope valid.
- The application service validates that Opportunity branch and organization match the referenced Family.
