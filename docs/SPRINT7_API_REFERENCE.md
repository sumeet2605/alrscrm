# Sprint 7 API Reference

Base path:

```text
/api/v1
```

## Staff Delivery APIs

| Method | Path | Permission | Purpose |
| --- | --- | --- | --- |
| `GET` | `/delivery/jobs` | `delivery:view` | List delivery jobs. |
| `POST` | `/delivery/jobs` | `delivery:create` | Create delivery job from ready EditingJob. |
| `GET` | `/delivery/jobs/{id}` | `delivery:view` | Get delivery job detail. |
| `PUT` | `/delivery/jobs/{id}` | `delivery:update` | Update delivery settings. |
| `POST` | `/delivery/jobs/{id}/generate-zip` | `delivery:update` | Mark ZIP generation completed. |
| `POST` | `/delivery/jobs/{id}/send` | `delivery:send` | Mark delivery sent and set `client_notified_at`. |
| `POST` | `/delivery/jobs/{id}/approve-reopen` | `delivery:reopen` | Approve client reopen request. |
| `GET` | `/delivery/jobs/{id}/downloads` | `delivery:download_audit` | List delivery download audit rows. |
| `GET` | `/delivery/metrics` | `delivery:dashboard` | Read delivery dashboard metrics. |

## Public Client APIs

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/delivery/client/{id}` | Read public client delivery state. |
| `POST` | `/delivery/client/{id}/download` | Record a client download. |
| `POST` | `/delivery/jobs/{id}/reopen-request` | Request delivery reopen. |

Public delivery APIs enforce delivery status, expiry, and download limits. They
do not use staff RBAC.

## Metrics

`GET /delivery/metrics` returns:

- `pending_delivery`
- `ready_delivery`
- `delivered`
- `expired`
- `reopened`
- `average_delivery_tat`
- `downloads_this_month`
- `re_download_revenue_potential`

