# Sprint 9 Architecture Review

Phase: pre-implementation architecture review only

No backend, frontend, migration, or test implementation changes were made.

## Review Scope

Sprint 9 proposes the Financial Management domain:

```text
Booking -> Invoice -> Payment -> Delivery Release
```

Reviewed against Sprint 1-8.1 implementation:

- Identity, Organizations, Branches, RBAC, and tenant-aware login
- Family customer profile aggregate
- Sales Opportunity pipeline
- Booking fulfillment aggregate
- Gallery selection aggregate and upgrade requests
- EditingJob production aggregate
- DeliveryJob delivery aggregate
- SaaS onboarding and platform-vs-tenant architecture review
- Existing migrations, routes, services, repositories, and frontend modules

## Executive Summary

Sprint 9 is architecturally valid, but implementation should not start until
the finance boundary decisions below are accepted.

The current system already contains some financial-like fields outside Finance:

- `Booking.total_amount`
- `Booking.advance_received`
- `Booking.balance_amount`
- `GalleryUpgradeRequest.price_per_photo`
- `GalleryUpgradeRequest.total_amount`
- `GalleryUpgradeRequest.status = PAID`
- `DeliveryJob.re_download_fee`
- Delivery metrics include `revenue_potential`

These fields must remain backward compatible, but Sprint 9 should make
`Invoice` and `Payment` the source of truth for new financial workflows.

Recommendation:

```text
STOP before implementation until the architecture decisions in this document
are accepted.
```

## Critical Architecture Findings

### 1. Booking Already Owns Payment-Like State

Evidence:

- `backend/app/bookings/models/booking.py`
- `backend/app/bookings/services/booking_service.py`
- `docs/SPRINT4_BOOKING_DOMAIN.md`

Current Booking stores:

```text
total_amount
advance_received
balance_amount
```

Sprint 9 says `Invoice` and `Payment` should own financial state. That is the
correct direction, but existing Booking fields cannot simply be removed without
breaking APIs and existing screens.

Decision required:

- Keep Booking totals as fulfillment/order snapshot fields for backward
  compatibility.
- Treat `Invoice.amount_paid` and `Invoice.balance_due` as the source of truth
  after an Invoice exists.
- Do not add new payment lifecycle state to Booking.
- Do not mutate Booking payment fields from Payment except through a deliberate
  compatibility sync, if one is explicitly approved.

### 2. Gallery Upgrade Requests Currently Have Payment State

Evidence:

- `backend/app/galleries/models/gallery.py`
- `backend/app/galleries/services/gallery_service.py`

Current Gallery upgrade requests store:

```text
price_per_photo
total_amount
status = PENDING | APPROVED | REJECTED | PAID
```

The Sprint 9 prompt explicitly says:

```text
Do not directly mutate payment fields on gallery.
```

Decision required:

- Keep Gallery upgrade request as an operational request.
- Do not use `GalleryUpgradeRequest.status = PAID` as financial truth going
  forward.
- Add Finance-owned invoices/line items for approved upgrade requests.
- If `mark_upgrade_paid` remains for compatibility, document it as legacy or
  replace the frontend workflow with Invoice/Payment.

### 3. Delivery Already Stores Re-Download Fee

Evidence:

- `backend/app/delivery/models/delivery.py`
- `backend/app/delivery/services/delivery_service.py`
- `docs/SPRINT7_DELIVERY_DOMAIN.md`

`DeliveryJob` stores:

```text
allow_re_download
re_download_fee
```

Sprint 7 documented this as policy state, not payment state. Sprint 9 should
preserve that boundary.

Decision required:

- Delivery may own re-download policy values.
- Invoice/Payment must own whether re-download fees were charged and collected.
- Delivery release gating must query Finance state instead of storing payment
  status inside DeliveryJob.

### 4. Platform And Tenant Separation Is Still In Transition

Evidence:

- `docs/PLATFORM_VS_TENANT_ARCHITECTURE_REVIEW.md`
- `backend/scripts/seed_super_admin.py`
- `backend/app/auth/service.py`
- `backend/app/identity/policies.py`

Current Super Admin is still modeled inside the `ALRSCRM` pseudo-organization.
Finance must be tenant-safe and branch-safe even while platform identity remains
transitional.

Decision required:

- Finance APIs must use the existing `AuthorizationContext` patterns for now.
- Platform admins may view/manage finance across tenants only through explicit
  platform authority.
- Tenant users must always be scoped by `organization_id` and, where relevant,
  `branch_id`.
- Future platform identity separation must not require rewriting Finance.

### 5. GST Configuration Does Not Exist Yet

Evidence:

- `backend/app/identity/models/organization.py`
- `backend/app/identity/schemas/organization.py`

`OrganizationSettings` currently stores studio profile fields, currency,
gallery defaults, and delivery defaults. It does not store:

- GSTIN
- billing name
- billing address
- GST registration state
- default tax rates
- intra-state/inter-state tax rules

Decision required:

- GST metadata should live in tenant organization settings or a Finance-owned
  tax settings/reference table.
- Tax percentages must not be hardcoded.
- Invoice should store calculated tax amounts as immutable invoice snapshot
  values.

## Aggregate Boundary Review

### Existing Aggregates

| Aggregate | Current Boundary | Sprint 9 Impact |
| --- | --- | --- |
| Organization | Tenant boundary and settings owner | Needs billing/GST settings or Finance settings reference. |
| Branch | Operational boundary | Finance records must be branch-scoped. |
| Family | Customer profile owner | Finance references `family_id`; must not duplicate profile fields except immutable invoice billing snapshot if approved. |
| Lead | Not implemented as a separate aggregate | Current Sales aggregate is `Opportunity`, not `Lead`. Sprint 9 should not assume Lead exists. |
| Opportunity | Sales pipeline root | No direct Finance mutation required. |
| Booking | Fulfillment/order aggregate | Finance references `booking_id`; Booking should not gain more financial lifecycle state. |
| BookingItem | Booking child entity | Invoice line items can be generated from BookingItems. |
| Gallery | Selection aggregate | Upgrade billing should create Finance line items, not Gallery payment state. |
| EditingJob | Production aggregate | No Finance ownership. |
| DeliveryJob | Delivery aggregate | Delivery release can depend on Finance, but Delivery should not own payment status. |

### New Sprint 9 Aggregates

Recommended new aggregate roots:

- `Invoice`
- `Payment`

Recommended child/reference entities:

- `InvoiceLineItem` as child of `Invoice`
- `TaxRate` or `FinanceTaxSetting` as database-driven reference/configuration
- Optional `InvoiceSequence` if sequence format becomes branch-aware beyond a
  raw PostgreSQL sequence

## Recommended Finance Boundary

```text
Organization
└── Branch
    ├── Booking
    │   └── BookingItem
    │
    ├── Invoice
    │   ├── InvoiceLineItem
    │   └── references Booking, Family, Organization, Branch
    │
    ├── Payment
    │   └── references Invoice, Organization, Branch
    │
    └── DeliveryJob
        └── release gate reads Invoice.balance_due
```

Rules:

- Invoice owns invoice totals, tax snapshot, amount paid, and balance due.
- Payment owns received amount, method, status, reference, and refund state.
- Completed payments update invoice balances transactionally.
- Booking remains the operational source for package/order line generation.
- Gallery upgrade requests become invoice source documents, not payment records.
- Delivery reads Finance state before `SENT` when payment enforcement is
  enabled.

## Required Architecture Decisions Before Code

### Decision 1: Booking Financial Compatibility

Recommended:

- Keep Booking monetary fields for existing behavior.
- Do not remove or rename them in Sprint 9.
- Do not add new payment state to Booking.
- Generate Invoice from Booking totals and BookingItems.
- Define whether `advance_received` should create an initial Payment or remain
  a legacy Booking snapshot.

Preferred Sprint 9 approach:

```text
If Booking has advance_received > 0 when invoice is created, create a completed
Payment only if an explicit migration/workflow decision is approved.
Otherwise keep advance_received as legacy booking state and require users to
record payments in Finance.
```

### Decision 2: Invoice Numbering

Required:

- Use PostgreSQL sequence-backed invoice numbers.
- No `count() + 1` logic.

Recommended format:

```text
INV-{YEAR}-{sequence:06d}
```

Branch-specific formatting can be added later, but the sequence itself must be
concurrency-safe.

### Decision 3: Payment Numbering

Required:

- Use sequence-backed payment numbers.
- No `count() + 1` logic.

Recommended format:

```text
PAY-{YEAR}-{sequence:06d}
```

### Decision 4: Tax Configuration

Required:

- Do not hardcode GST percentages.
- Store tax rates/configuration in database settings or a Finance tax reference
  table.

Recommended:

- Add organization/branch finance settings for GSTIN, billing name, billing
  address, and default tax mode.
- Add `tax_rates` table or equivalent reference records for CGST/SGST/IGST.
- Store invoice tax amounts as immutable snapshots.

### Decision 5: Delivery Release Gate

Required:

- Add `REQUIRE_PAYMENT_BEFORE_DELIVERY`.
- If enabled, `send_delivery()` must verify that all required invoices for the
  booking or delivery have `balance_due = 0`.

Recommended:

- Implement the check in Delivery service through a Finance query service.
- Do not add `payment_status` to `DeliveryJob`.
- Define whether the gate checks:
  - only the primary booking invoice, or
  - all non-void invoices for the booking/delivery.

Preferred Sprint 9 rule:

```text
Delivery cannot move to SENT if any ISSUED, PARTIALLY_PAID, OVERDUE, or DRAFT
invoice linked to the booking has balance_due > 0.
VOID invoices are ignored.
```

### Decision 6: Gallery Upgrade Billing

Required:

- Additional photos, albums, premium edits, extra downloads, and other add-ons
  should become invoice line items.

Recommended:

- Keep `GalleryUpgradeRequest` operational.
- Add `invoice_id` or source metadata on invoice line items, not payment state
  on Gallery.
- Avoid adding more upgrade payment statuses to Gallery.

### Decision 7: Platform Vs Tenant

Required:

- Finance must work with the current pseudo-platform Super Admin but should not
  encode assumptions that `ALRSCRM` is a real tenant.

Recommended:

- All Finance rows require `organization_id` and `branch_id`.
- Platform admin access uses `context.is_platform_admin`.
- Tenant user access filters by organization and branch.
- Future platform identity separation should require only auth/RBAC changes,
  not Finance schema changes.

## Proposed Database Design

### `invoices`

Required columns:

- `id`
- `invoice_number`
- `organization_id`
- `branch_id`
- `family_id`
- `booking_id`
- `invoice_status`
- `subtotal`
- `discount_amount`
- `taxable_amount`
- `cgst_amount`
- `sgst_amount`
- `igst_amount`
- `total_amount`
- `amount_paid`
- `balance_due`
- `currency`
- `issue_date`
- `due_date`
- `notes`
- `created_by_user_id`
- `created_at`
- `updated_at`

Recommended additions:

- `voided_at`
- `voided_by_user_id`
- `issued_at`
- `paid_at`
- `deleted_at` only if soft-delete is required; otherwise use `VOID`.

Recommended constraints:

- `invoice_number` unique.
- Non-negative monetary columns.
- `amount_paid <= total_amount`.
- `balance_due >= 0`.
- `balance_due = total_amount - amount_paid` should be enforced in service and
  tested; database generated columns can be considered later.
- `organization_id + branch_id` FK to branches.

### `invoice_line_items`

Required columns:

- `id`
- `invoice_id`
- `description`
- `quantity`
- `unit_price`
- `discount_amount`
- `tax_rate`
- `line_total`
- `service_type`

Recommended additions:

- `source_type`
- `source_id`
- `taxable_amount`
- `cgst_amount`
- `sgst_amount`
- `igst_amount`

### `payments`

Required columns:

- `id`
- `payment_number`
- `organization_id`
- `branch_id`
- `invoice_id`
- `amount`
- `payment_method`
- `payment_status`
- `transaction_reference`
- `received_date`
- `notes`
- `received_by_user_id`
- `created_at`

Recommended additions:

- `refunded_at`
- `refund_reference`
- `failed_reason`

Recommended constraints:

- `payment_number` unique.
- `amount >= 0`.
- `organization_id + branch_id` FK to branches.
- `invoice_id` indexed.

### Finance Settings

Recommended table:

```text
finance_settings
```

Suggested columns:

- `organization_id`
- `branch_id` nullable for organization default
- `gstin`
- `billing_name`
- `billing_address`
- `default_currency`
- `default_due_days`
- `auto_create_booking_invoice`
- `require_payment_before_delivery`

This is preferable to putting all finance configuration in environment
variables because these behaviors are tenant/branch business settings.

Environment variables may still provide platform defaults:

- `AUTO_CREATE_BOOKING_INVOICE`
- `REQUIRE_PAYMENT_BEFORE_DELIVERY`

## API Impact Review

Required new routers:

- `/api/v1/invoices`
- `/api/v1/payments`
- `/api/v1/finance/metrics`

Required route behavior:

- All list routes must scope by organization and branch.
- Platform admins may query across organizations only intentionally.
- Tenant users must never pass arbitrary `organization_id` to escape scope.
- Branch-scoped users must be constrained to their branch.
- Public routes should not expose Finance data.

Required API operations:

```text
GET /api/v1/invoices
POST /api/v1/invoices
GET /api/v1/invoices/{id}
PUT /api/v1/invoices/{id}
POST /api/v1/invoices/{id}/issue
POST /api/v1/invoices/{id}/void

GET /api/v1/payments
POST /api/v1/payments
GET /api/v1/payments/{id}
POST /api/v1/payments/{id}/refund

GET /api/v1/finance/metrics
```

Recommended additional API:

```text
GET /api/v1/finance/tax-summary
GET /api/v1/finance/settings
PATCH /api/v1/finance/settings
POST /api/v1/invoices/from-booking/{booking_id}
POST /api/v1/invoices/from-gallery-upgrade/{upgrade_request_id}
```

The extra APIs should be added only if needed for the frontend workflow. The
core prompt does require a tax summary API, so it should be included in the
Sprint 9 contract.

## Frontend Impact Review

Required new frontend module:

```text
frontend/src/modules/finance
```

Required pages:

- Finance Dashboard
- Invoice List
- Invoice Detail
- Payment List
- Payment Detail
- Outstanding Report
- Revenue Report

Required routes:

- `/finance`
- `/finance/invoices`
- `/finance/invoices/:id`
- `/finance/payments`
- `/finance/payments/:id`

Required navigation:

```text
Finance
  Dashboard
  Invoices
  Payments
```

Required frontend concerns:

- Use generated OpenAPI types where possible.
- Keep finance API adapters separate from bookings, galleries, and delivery.
- Do not derive paid/unpaid state from Booking, Gallery, or Delivery UI fields
  once Finance is introduced.
- Hide Finance navigation from Editor and Photographer.
- Include Branch Manager branch-scoped visibility.

## RBAC Impact Review

Required permissions:

- `finance:view`
- `finance:create_invoice`
- `finance:update_invoice`
- `finance:void_invoice`
- `finance:create_payment`
- `finance:refund_payment`
- `finance:dashboard`

Required roles:

| Role | Finance Access |
| --- | --- |
| Super Admin | Full platform access. |
| Organization Admin | Full tenant finance access. |
| Owner | Full tenant finance access. |
| Branch Manager | Branch finance access. |
| Sales Executive | No finance access unless explicitly expanded later. |
| Photographer | No finance access. |
| Editor | No finance access. |
| Customer Success | No finance access unless explicitly expanded later. |

Recommendation:

- Do not grant finance permissions to Sales Executive by default.
- Keep backend permissions authoritative.
- Frontend route permissions must mirror but not replace backend enforcement.

## Migration Impact Review

Sprint 9 likely needs one migration for the initial Finance schema:

- Create invoice sequence.
- Create payment sequence.
- Create invoices.
- Create invoice line items.
- Create payments.
- Create finance settings or tax reference tables.
- Add indexes for tenant/branch/date/status queries.

Potential second migration:

- Link gallery upgrade requests to finance source documents if needed.
- Add invoice/payment references to delivery artifacts only if required. This
  is not recommended for Sprint 9 unless the domain flow demands it.

Migration concerns:

- Do not alter existing Booking monetary columns in Sprint 9.
- Do not drop `GalleryUpgradeRequest.total_amount` or status values in Sprint 9.
- Do not add payment status to DeliveryJob.
- Backfill is optional. Existing bookings do not need invoices unless a
  migration/backfill business rule is explicitly approved.

## Metrics Impact Review

Required metrics:

- Revenue This Month
- Revenue This Year
- Outstanding Amount
- Paid Amount
- Overdue Amount
- Invoices By Status
- Payments By Method
- Revenue By Service Type
- Branch Revenue
- Average Collection Time

Recommended metric definitions:

- Revenue should count completed payments, not issued invoice total.
- Outstanding amount should use non-void invoice `balance_due`.
- Overdue amount should use due date and unpaid balance.
- Revenue by service type should use invoice line items tied to completed
  payments or paid invoice allocation rules.
- Average collection time should measure from invoice issue date to fully paid
  date.

Decision required:

- Define how partial payments are allocated across invoice line items for
  service-type revenue reporting.

Preferred Sprint 9 simplification:

```text
Revenue by service type uses fully paid invoices only.
Partial payment allocation can be a future enhancement.
```

## Test Impact Review

Required backend tests:

- Cross-tenant invoice access denied.
- Cross-tenant payment access denied.
- Branch-scoped invoice access denied outside branch.
- Branch-scoped payment access denied outside branch.
- Overpayment rejected.
- Payment against VOID invoice rejected.
- Completed payment updates invoice balances.
- Payment before delivery enforcement blocks `SENT`.
- Invoice sequence generation is not count-based.
- Finance dashboard metrics are tenant and branch scoped.
- Invoice totals become immutable after payment exists.
- Void invoice cannot receive payment.
- GST/tax summary calculation uses configured rates.

Required frontend tests:

- Finance navigation visible to Owner/Organization Admin/Branch Manager.
- Finance navigation hidden from Editor and Photographer.
- Invoice list route protection.
- Invoice creation workflow.
- Payment creation workflow.
- Dashboard metrics rendering.

## Security And Multi-Tenant Review

Finance is high-sensitivity data. Required safeguards:

- Every Finance row must include `organization_id` and `branch_id`.
- Every repository query must apply tenant and branch scope.
- Every mutation must validate referenced Booking/Family/Invoice belongs to the
  same organization and branch.
- Public Gallery and Delivery endpoints must not expose invoices or payments.
- Audit events must include organization and branch scope.
- Platform Super Admin access must remain explicit and auditable.

## Audit Events

Required audit-backed events:

- `invoice.created`
- `invoice.issued`
- `invoice.voided`
- `payment.created`
- `payment.completed`
- `payment.refunded`

Recommended additions:

- `invoice.updated`
- `invoice.overdue_marked`
- `payment.failed`

These remain audit-backed events. No outbox or event bus should be introduced
unless separately approved.

## Implementation Plan After Approval

### Phase 1: Finance Domain Backend

- Add finance enums, models, schemas, repositories, services, routes.
- Add migrations for sequences, invoices, line items, payments, settings/tax
  references.
- Add RBAC permissions and seeds.
- Wire Finance router.
- Add audit events.

### Phase 2: Booking And Gallery Integration

- Add optional draft invoice creation from confirmed Booking.
- Add invoice generation from approved Gallery upgrade requests.
- Preserve legacy Booking/Gallery fields.
- Avoid writing Finance state into Booking/Gallery.

### Phase 3: Delivery Release Gate

- Add finance query service for outstanding balance.
- Enforce payment gate in `send_delivery()` only when configured.
- Add tests for enabled and disabled gate behavior.

### Phase 4: Frontend Finance Module

- Add Finance navigation, routes, pages, API adapter, and types.
- Use generated OpenAPI types where possible.
- Add frontend tests.

### Phase 5: Verification

Run:

```bash
ruff check backend frontend
ruff format --check backend frontend
python -m pytest backend/tests
cd frontend
npm run lint
npm run test
npm run build
npm run generate:api-types
cd ..
docker compose up -d --build
docker compose exec api alembic upgrade head
```

## Stop Conditions Before Implementation

Implementation should not start until these are accepted:

1. Booking monetary fields remain backward-compatible snapshots.
2. Invoice/Payment become the source of truth for new financial workflows.
3. Gallery upgrade `PAID` status is treated as legacy or operational, not
   authoritative Finance state.
4. Delivery payment gate reads Finance state and does not store payment status.
5. GST/tax percentages are database-driven, not hardcoded.
6. Finance settings ownership is decided.
7. Partial payment allocation rules for revenue by service type are accepted or
   deferred.
8. Platform-vs-tenant transition is acknowledged and Finance remains tenant
   scoped.

## Recommendation

```text
NO-GO for immediate Sprint 9 implementation until the stop conditions are
accepted.
```

```text
GO for Sprint 9 implementation after accepting the finance boundary decisions
above.
```

The domain should be implemented as a new Finance bounded context with
`Invoice` and `Payment` aggregate roots. Existing Booking, Gallery, Editing,
and Delivery aggregates should reference or query Finance but must not own
additional financial lifecycle state.
