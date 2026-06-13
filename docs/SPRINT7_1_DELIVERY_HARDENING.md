# Sprint 7.1 Delivery Hardening

Sprint 7.1 hardens Delivery Management for private client photo delivery.

## Completed Scope

- Public delivery URLs now use opaque access tokens instead of delivery IDs.
- Access tokens are generated with cryptographic entropy and stored as hashes.
- Raw access tokens are returned only through one-time staff responses after
  send, rotate, or reopen approval.
- Delivery access tokens support expiry, revocation, rotation, and last-access
  tracking.
- Password-protected delivery is supported with bcrypt hashes.
- Public downloads require a temporary delivery session token.
- Public delivery route is `/client/delivery/{token}`.
- Reopen requests require name, email, and reason.
- Reopen requests are accepted only for delivered jobs.
- Reopen cooldown is enforced at one request per delivery every 24 hours.
- Reopen rate limit is enforced at five requests per IP per day.
- Delivery lifecycle state changes are routed through explicit command
  endpoints.
- Generic delivery update no longer accepts delivery or ZIP status fields.
- Delivery ZIP generation creates a stored artifact and returns signed download
  URLs.
- Delivery numbers use a PostgreSQL sequence in production.
- Delivery audit rows now carry `organization_id` and `branch_id`.
- Frontend public delivery page supports invalid, expired, password-protected,
  reopen-request, and artifact-download states.

## Backend Changes

- Added delivery access token persistence.
- Added delivery artifact persistence.
- Added reopen-attempt persistence.
- Added delivery password hash and reopen-request timestamp to delivery jobs.
- Added tenant and branch columns to delivery audits.
- Added public delivery authentication endpoint.
- Added staff access-token rotate and revoke endpoints.
- Added staff close delivery endpoint.

## Frontend Changes

- Client delivery now treats the route parameter as an access token.
- Password-protected deliveries show an unlock prompt.
- Downloads request a temporary delivery session before requesting a signed
  artifact URL.
- Reopen request form collects required client identity and reason fields.
- Staff detail page shows one-time secure links, artifact history, download
  audit, token rotation, token revocation, and close actions.
- Delivery action buttons are hidden for view-only delivery roles.

## Non-Goals

Sprint 7.1 does not implement:

- Payments
- Invoices
- WhatsApp
- AI
- Sprint 8 capabilities
- A general event bus or outbox

