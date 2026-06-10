# Sprint 4 Database Design

Migration:

- `backend/alembic/versions/202606100007_create_booking_fulfillment.py`

## Tables Added

### `packages`

Branch-scoped package reference data.

Important columns:

- `organization_id`
- `branch_id`
- `name`
- `service_type`
- `price`
- `is_active`

Constraints and indexes:

- Unique package name per branch
- Non-negative price
- Indexes on `branch_id` and `service_type`

### `package_addons`

Branch-scoped addon reference data.

Constraints and indexes:

- Unique addon name per branch
- Non-negative price
- Index on `branch_id`

### `bookings`

Fulfillment aggregate root.

Important columns:

- `family_id`
- `opportunity_id`
- `booking_number`
- `booking_status`
- `total_amount`
- `advance_received`
- `balance_amount`
- `booking_date`
- `deleted_at`

Constraints and indexes:

- Unique `booking_number`
- Non-negative total, advance, and balance
- Indexes on `family_id`, `opportunity_id`, `booking_status`, `booking_date`,
  and `(branch_id, booking_date)`

### `booking_items`

Booking-owned package lines.

Constraints and indexes:

- Non-negative price, discount, and final amount
- Indexes on `booking_id` and `service_type`

### `booking_item_addons`

BookingItem-owned addon selections.

Constraints and indexes:

- Non-negative price
- Index on `booking_item_id`

### `shoot_schedules`

BookingItem-owned shoot schedule.

Constraints and indexes:

- `scheduled_end > scheduled_start`
- Indexes on `booking_id`, `booking_item_id`, `scheduled_start`, and
  `shoot_status`

### `photographer_assignments`

ShootSchedule-owned photographer assignments.

Constraints and indexes:

- Unique `(shoot_schedule_id, user_id)`
- Indexes on `user_id`, `assigned_at`, and `shoot_schedule_id`

## Modeling Notes

- Booking stores references to Family and Opportunity, not copied customer
  profile fields.
- Totals are calculated in the application service and persisted as aggregate
  state.
- Package and Addon prices are snapshotted into booking item rows at booking
  creation/update time.
- Payments are not implemented; `advance_received` is a booking field only.
