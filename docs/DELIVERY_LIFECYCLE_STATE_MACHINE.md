# Delivery Lifecycle State Machine

Delivery state changes must go through explicit command endpoints.

Generic update APIs must not mutate:

- `delivery_status`
- `zip_generation_status`

## States

```text
PENDING
ZIP_GENERATING
READY
SENT
DELIVERED
EXPIRED
REOPEN_REQUESTED
REOPENED
CLOSED
```

## ZIP States

```text
PENDING
GENERATING
COMPLETED
FAILED
```

## Allowed Transitions

| Command | From | To |
| --- | --- | --- |
| Create DeliveryJob | EditingJob `READY_FOR_DELIVERY` | `PENDING` |
| Generate ZIP | `PENDING`, `REOPENED` | `ZIP_GENERATING` then `READY` |
| Send Delivery | `READY`, `REOPENED` | `SENT` |
| Client Download | `READY`, `SENT` | `DELIVERED` |
| Client Download | `DELIVERED`, `REOPENED` | unchanged |
| Expiry Check | active non-closed states after expiry date | `EXPIRED` |
| Request Reopen | `DELIVERED` | `REOPEN_REQUESTED` |
| Approve Reopen | `REOPEN_REQUESTED` | `REOPENED` |
| Close Delivery | `DELIVERED`, `EXPIRED`, `REOPENED` | `CLOSED` |

## Rejected Transitions

- Public reopen from `READY`, `SENT`, `ZIP_GENERATING`, `EXPIRED`, or `CLOSED`.
- Staff send before ZIP generation completes.
- Public download before artifact generation.
- Public download after token expiry or revocation.
- Generic update directly setting delivery or ZIP status.

