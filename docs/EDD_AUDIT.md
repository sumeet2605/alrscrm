# EDD Audit

EDD means `expected_delivery_date` on the Family aggregate.

Audit scope:

- Database persistence
- ORM model
- Backend schemas
- Create and update APIs
- Frontend forms
- Frontend detail and list pages
- Search and filter support

## Fully Implemented

### Database Persistence

- Migration `202606100004_create_family_domain.py` creates
  `families.expected_delivery_date` as a nullable `Date`.
- Migration creates `ix_families_expected_delivery_date`.

### ORM Model

- `backend/app/families/models/family.py` defines
  `Family.expected_delivery_date` as a nullable indexed date column.

### Backend Schemas

- `FamilyBase` includes `expected_delivery_date`.
- `FamilyCreate` inherits EDD support.
- `FamilyUpdate` includes EDD support.
- `FamilyRead` returns EDD.

### Create And Update APIs

- `POST /api/v1/families` accepts EDD through `FamilyCreate`.
- `PUT /api/v1/families/{family_id}` accepts EDD through `FamilyUpdate`.
- Repository create and update paths persist scalar fields, including EDD.

### List API Filtering

- `GET /api/v1/families` supports:
  - `edd_from`
  - `edd_to`
- Repository filtering applies inclusive lower and upper date bounds.

### Frontend Forms

- `FamilyFormPage` includes an `Expected Delivery Date` `DatePicker`.
- Create and edit payloads serialize the date as `YYYY-MM-DD`.
- Edit mode hydrates EDD back into a `dayjs` value.

### Frontend Detail Pages

- `FamilyDetailsPage` displays EDD in the profile summary.

### Frontend List Pages

- `FamilyListPage` displays EDD in the table.
- `FamilyListPage` supports EDD range filtering through `RangePicker`.
- EDD table sorting is implemented client-side for loaded rows.

### Generated Types

- `frontend/src/types/generated/openapi.ts` includes EDD in family create,
  update, read, and list query parameter contracts.

## Partially Implemented

- EDD changes are not emitted as a discrete domain event. Current behavior is
  covered by the existing `family.updated` audit event.
- EDD search is range-filter based only. It is not part of the
  `/families/search` endpoint, which searches identity/contact fields.
- EDD has no dashboard KPI, notification, or reminder workflow.

## Missing

- No dedicated `ExpectedDeliveryDateChanged` event.
- No EDD timeline/history.
- No EDD reminder or overdue delivery dashboard.
- No EDD-specific API endpoint.
- No backend test dedicated only to EDD range filtering was found.

## Recommended Sprint

EDD is sufficiently wired for Sprint 2 Family profile management and current
frontend usage.

Recommended future sprint:

- Add EDD lifecycle/history and notification behavior in a Delivery Management
  sprint, after the Delivery aggregate exists.
- Add dedicated EDD range filter tests as low-risk backend test hardening.

No new EDD functionality was implemented as part of this audit.
