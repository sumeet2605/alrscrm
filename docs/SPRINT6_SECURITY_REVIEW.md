# Sprint 6 Security Review

Reviewed areas:

- `EditingJob`
- `EditingReview`
- `GalleryUpgradeRequest`
- Gallery selection submission hooks
- Tenant and branch isolation
- Production frontend route access

## Summary

No critical or major open security issue remains for Sprint 6 readiness.

The implementation relies on route-level permissions plus service-level tenant
and branch enforcement. Tests now cover cross-tenant EditingJob access denial
and branch-scoped GalleryUpgradeRequest access.

## Controls Verified

| Area | Status | Notes |
| --- | --- | --- |
| Editing route RBAC | Passed | Routes use `require_permissions(...)`. |
| Tenant isolation | Passed | `EditingJob` access checks organization scope. |
| Branch isolation | Passed | Branch-scoped callers are constrained to their branch. |
| Editor scope | Passed | Editor-limited users can only access assigned work. |
| Self approval | Passed | Assigned editor cannot approve or reject own job. |
| Ready job immutability | Passed | Ready-for-delivery update returns `400`. |
| Gallery upgrade request scope | Passed | Upgrade requests persist and query by organization and branch. |
| Public gallery favorite selection | Improved | Favorite button has accessible label; storage access remains governed by existing gallery URL behavior. |

## Permissions

Seeded Sprint 6 permissions:

- `galleries:reopen`
- `editing:view`
- `editing:create`
- `editing:update`
- `editing:assign`
- `editing:review`
- `editing:approve`
- `editing:dashboard`

Role behavior:

- Super Admin, Organization Admin, Owner, and Branch Manager can manage editing
  within their scope.
- Editor can view, update, review, and access dashboard workload.
- Editor does not receive `editing:approve`.

## Findings Closed During Validation

### Ready-For-Delivery Update Semantics

Before validation, ready-for-delivery update attempts returned `409 Conflict`.
Sprint 6 requirements expected `400` or `403`. The service now returns
`400 Bad Request`, and regression coverage was added.

### Cross-Tenant EditingJob Regression Coverage

Explicit coverage was added to prove an owner from another organization cannot
read an EditingJob outside their tenant.

### Public Gallery Favorite Accessibility

The favorite button had no accessible name. It now exposes `Select photo` or
`Photo selected`, improving keyboard/screen-reader discoverability and test
stability.

## Residual Risks

- Generated API responses still use the generic `APIResponse` envelope, which
  limits static precision for generated frontend types.
- There is no outbox or event bus. Audit rows must not be treated as durable
  integration events.
- Editing permissions should be validated during startup after seed execution.
- Additional branch-crossing EditingJob tests should be added for defense in
  depth.

## Verdict

Sprint 6 security posture is acceptable for release readiness within the
implemented editing workflow.
