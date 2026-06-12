# Sprint 9.4 Monitoring Strategy

## Current State

The application currently has a basic health endpoint and standard process
logging. There is no metrics endpoint, request correlation, structured access
logging, alerting integration, or centralized log strategy in the repository.

## Sprint 9.4 Monitoring Additions

- Structured JSON API access logs.
- Request ID generation and response headers.
- In-process operational metrics.
- Super Admin metrics endpoint:

```text
GET /api/v1/platform/health/metrics
```

## Metrics Captured

- API latency
- Error rate
- Database readiness latency
- Storage readiness latency
- Invoice creation count
- Payment creation count
- Gallery access count
- Delivery count

## Logging Fields

Structured logs should include:

- `timestamp`
- `request_id`
- `organization_id`
- `branch_id`
- `user_id`
- `route`
- `duration_ms`
- `status_code`

Secrets must never be logged.

## Production Alert Recommendations

| Signal | Alert |
| --- | --- |
| API readiness failure | Page on-call |
| Database latency spike | Warn and investigate |
| Storage latency spike | Warn and investigate |
| Error rate spike | Page if sustained |
| Auth failure spike | Security alert |
| Public Gallery access spike | Security alert |
| Delivery download spike | Security alert |
| Invoice/payment failure | Business operations alert |

## Remaining Gaps After Sprint 9.4

- External metrics backend.
- Centralized log sink.
- Tracing.
- Alert manager.
- Dashboards.
- Uptime checks.

Sprint 9.4 prepares the application to emit useful signals. Production
deployment must wire those signals into the chosen observability platform.
