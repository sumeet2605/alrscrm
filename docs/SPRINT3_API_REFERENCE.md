# Sprint 3 API Reference

All endpoints use `/api/v1` and the existing response envelope.

## Opportunities

- `POST /api/v1/opportunities`
- `GET /api/v1/opportunities`
- `GET /api/v1/opportunities/{id}`
- `PUT /api/v1/opportunities/{id}`
- `DELETE /api/v1/opportunities/{id}`

Filters:

- `search`
- `stage`
- `assigned_to_user_id`
- `opportunity_type`
- `lost_reason_id`
- `branch_id`

Search matches Family name, phone, Family code, and opportunity type.

## Pipeline

- `GET /api/v1/opportunities/pipeline`

Returns grouped Opportunities by:

- `NEW`
- `PACKAGE_SENT`
- `INTERESTED`
- `NEED_FOLLOW_UP`
- `THINKING`
- `BOOKED`
- `LOST`

## Metrics

- `GET /api/v1/opportunities/metrics`

Returns:

- Open Opportunities
- Booked Opportunities
- Lost Opportunities
- Conversion Rate
- Pending Follow Ups
- Missed Follow Ups
- Follow Up Compliance
- Average Opportunity Value

## Follow Ups

- `POST /api/v1/followups`
- `GET /api/v1/followups`
- `PUT /api/v1/followups/{id}`

Filters:

- `status`
- `assigned_to_user_id`
- `branch_id`
- `due_from`
- `due_to`

## Notes

- `POST /api/v1/opportunities/{id}/notes`
- `GET /api/v1/opportunities/{id}/notes`

## Stage History

- `GET /api/v1/opportunities/{id}/history`

## Lost Reasons

- `GET /api/v1/lost-reasons`
