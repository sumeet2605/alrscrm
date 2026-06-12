# Organization Aggregate Diagram

```text
Organization
├── OrganizationSettings
├── Branch
└── User membership references
```

## Boundary Rules

`Organization` is the tenant aggregate root.

It owns:

- Active state
- Organization settings
- Branches

It references or is referenced by:

- Users
- Families
- Opportunities
- Bookings
- Galleries
- Editing jobs
- Delivery jobs

Business aggregates outside Organization must store `organization_id` and, when
branch-owned, `branch_id`.

## Not Inside Organization Aggregate

These remain separate aggregates or entities:

- Family
- Opportunity
- Booking
- Gallery
- EditingJob
- DeliveryJob
- RefreshTokenSession
- AuditLog

