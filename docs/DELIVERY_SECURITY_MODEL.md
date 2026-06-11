# Delivery Security Model

## Public Access

Client delivery access uses opaque tokens:

```text
/client/delivery/{token}
```

The token is not the delivery job ID. The backend stores only a SHA-256 token
identifier and returns the raw token only once after token creation or rotation.

Token validation requires:

- Token hash exists.
- Token is not revoked.
- Token is not expired.
- Referenced delivery job exists.
- Delivery job is in a client-accessible state.

Invalid, revoked, or expired tokens return `401` or `410` depending on the
failure mode.

## Password Protection

Delivery passwords are optional.

When configured:

- Passwords are stored as bcrypt hashes.
- Plaintext passwords are never returned by APIs.
- Public clients must call:

```text
POST /api/v1/delivery/public/authenticate
```

Request:

```json
{
  "token": "raw-delivery-token",
  "password": "client-password"
}
```

The response contains a temporary delivery session token valid for 24 hours.

## Downloads

Downloads require:

- A valid public access token.
- A valid temporary delivery session token.
- An active delivery artifact.
- Remaining download quota.

The download endpoint returns a signed artifact URL instead of exposing storage
metadata directly.

## Token Rotation And Revocation

Staff users with delivery send permission can rotate or revoke delivery access
tokens.

Rotation:

- Revokes active tokens for the job.
- Creates a new hashed token record.
- Returns a one-time raw public URL in the staff response.

Revocation:

- Marks active tokens revoked.
- Does not delete token audit history.

## Audit

Delivery audit rows include:

- `organization_id`
- `branch_id`
- `delivery_job_id`
- `event_type`
- `event_timestamp`
- `event_details`

Audit-backed delivery events include:

- `delivery.created`
- `delivery.generated`
- `delivery.sent`
- `delivery.downloaded`
- `delivery.reopen_requested`
- `delivery.reopen_approved`
- `delivery.closed`

