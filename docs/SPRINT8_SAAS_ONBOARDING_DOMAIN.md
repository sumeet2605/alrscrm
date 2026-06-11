# Sprint 8 SaaS Onboarding Domain

Sprint 8 introduces SaaS Organization Onboarding for ALRSCRM.

## Platform Boundary

`ALRSCRM` is the platform tenant.

It is used for:

- Platform administration
- SaaS operations
- Support
- Future billing
- Future feature flags
- Future global settings

## Customer Tenant Boundary

Customer studios are Organizations.

Examples:

- Alluring Lens Studios
- Little Smiles Photography
- Baby Moments Studio
- Newborn Stories

Each customer Organization owns:

- Branches
- Users
- Families
- Opportunities
- Bookings
- Galleries
- Editing jobs
- Delivery jobs

## Organization Aggregate

`Organization` is the tenant aggregate root.

Owned entities:

- `OrganizationSettings`
- `Branch`

Related identity entity:

- `User`

Onboarding creates the first Owner user in the same transaction, but User
remains part of Identity and Access.

## Onboarding Command

The onboarding command creates:

1. Organization
2. Organization Settings
3. Default Branch
4. Owner User
5. Owner role assignment

All records are created in one backend transaction.

## RBAC

Only `Super Admin` can onboard organizations.

`Organization Admin` cannot create tenants.

## Non-Goals

Sprint 8 does not implement:

- Payments
- Subscriptions
- Public self-signup
- Tenant-aware login changes
- Separate databases
- Separate schemas

