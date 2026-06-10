# Sprint 4 API Reference

All endpoints are under `/api/v1`.

## Bookings

### `POST /bookings`

Creates a Booking from a `BOOKED` Opportunity.

Required:

- `organization_id`
- `branch_id`
- `family_id`
- `opportunity_id`
- `booking_date`
- at least one `items[]`

Calculated:

- `total_amount`
- `balance_amount`
- booking number

### `GET /bookings`

Supports:

- Search by booking number, family name, family code, phone, and opportunity
  type
- Filters by booking status, service type, photographer, date range, and branch
- Pagination

### `GET /bookings/{id}`

Returns booking details, family summary, opportunity summary, items, addons, and
item schedules.

### `PUT /bookings/{id}`

Updates mutable booking fields and optionally replaces booking items.

Cancelled bookings are read-only.

### `DELETE /bookings/{id}`

Soft deletes a booking.

### `GET /bookings/metrics`

Returns:

- Total Bookings
- Upcoming Shoots
- Completed Shoots
- Cancelled Shoots
- Revenue Booked
- Average Booking Value
- Photographer Utilization

## Packages

- `POST /packages`
- `GET /packages`
- `GET /packages/{id}`
- `PUT /packages/{id}`

## Addons

- `POST /addons`
- `GET /addons`
- `PUT /addons/{id}`

## Schedules

- `POST /schedules`
- `GET /schedules`
- `GET /schedules/{id}`
- `PUT /schedules/{id}`

Schedules are scoped by Booking and BookingItem.

## Assignments

- `POST /assignments`
- `GET /assignments`
- `DELETE /assignments/{id}`

Sales Executive users do not have photographer assignment write permission.
Photographer users see assigned shoot schedules.
