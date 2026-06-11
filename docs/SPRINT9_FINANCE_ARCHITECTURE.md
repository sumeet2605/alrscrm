# Sprint 9 Finance Architecture

Phase: architecture review only

No code, migrations, or runtime behavior were changed.

## Decision

Recommendation:

```text
GO WITH CHANGES
```

Sprint 9 can proceed after the boundary decisions in
`docs/SPRINT9_FINANCE_BOUNDARY_REVIEW.md` are accepted.

Finance should be implemented as a separate bounded context and become the
source of truth for:

- Invoices
- Invoice line items
- Payments
- Receivables
- Credit notes
- Debit notes
- GST snapshots
- Revenue reporting
- Tax reporting

Finance must not push financial lifecycle state into:

- Bookings
- Galleries
- Editing
- Delivery

Those domains may reference Finance or request Finance actions, but they should
not own invoice, payment, tax, refund, credit note, debit note, or receivable
state.

## Current Architecture Readiness

The current architecture is ready to add a Finance bounded context because:

- `organization_id` is consistently used as tenant boundary.
- `branch_id` is consistently used as operational boundary.
- Tenant-aware login exists.
- Audit logs now support tenant and branch scope.
- Booking, Gallery, Editing, and Delivery are already separate bounded
  contexts.
- Delivery and Gallery public access are hardened and do not require Finance
  data exposure.

The architecture is not ready for immediate Finance implementation until these
decisions are accepted:

- Booking monetary fields become compatibility snapshots, not financial truth.
- Gallery upgrade payment state becomes legacy or operational state, not
  financial truth.
- Delivery re-download fee remains delivery policy, while Finance bills and
  collects it.
- GST settings and rates are database-driven, versioned, and effective dated.
- Platform finance is kept separate from tenant finance.

## Existing Financial Fields

| Domain | Entity | Field | Purpose | Recommended Owner |
| --- | --- | --- | --- | --- |
| Organization | OrganizationSettings | `currency` | Tenant currency default | FinanceSettings or OrganizationSettings |
| Sales | Opportunity | `estimated_value` | Sales forecast | Sales |
| Booking | Package | `price` | Package catalog price | Booking catalog |
| Booking | PackageAddon | `price` | Addon catalog price | Booking catalog |
| Booking | Booking | `total_amount` | Booking order snapshot | Booking snapshot, not Finance truth |
| Booking | Booking | `advance_received` | Legacy advance amount | Payment going forward |
| Booking | Booking | `balance_amount` | Legacy computed balance | Invoice going forward |
| Booking | BookingItem | `price` | Package price snapshot | Booking snapshot |
| Booking | BookingItem | `discount` | Booking item discount | Booking snapshot and Invoice source |
| Booking | BookingItem | `final_amount` | Booking item final amount | Booking snapshot and Invoice source |
| Booking | BookingItemAddon | `price` | Addon price snapshot | Booking snapshot |
| Gallery | GalleryUpgradeRequest | `price_per_photo` | Upgrade quote input | Gallery operational quote |
| Gallery | GalleryUpgradeRequest | `total_amount` | Upgrade quote total | Invoice line item going forward |
| Gallery | GalleryUpgradeRequest | `status = PAID` | Payment-like marker | Finance should replace as truth |
| Delivery | DeliveryJob | `re_download_fee` | Re-download policy price | Delivery policy, Finance billing |
| Delivery | Delivery metrics | `revenue_potential` | Potential re-download revenue | Finance reporting going forward |

## Finance Bounded Context

Recommended package:

```text
backend/app/finance
```

Recommended frontend module:

```text
frontend/src/modules/finance
```

Recommended backend structure:

```text
backend/app/finance
├── enums.py
├── models
│   ├── __init__.py
│   └── finance.py
├── repositories.py
├── routes.py
├── schemas
│   ├── __init__.py
│   └── finance.py
└── services
    ├── __init__.py
    └── finance_service.py
```

## Aggregate Roots

### FinanceSettings

`FinanceSettings` is a tenant or branch finance configuration entity. It may be
modeled as an aggregate root if settings are independently managed.

Owns:

- GST registration profile
- Billing identity
- Default invoice due days
- Default invoice prefix
- Payment-before-delivery setting
- Auto-create booking invoice setting

Scope:

- `organization_id` required
- `branch_id` nullable for organization default

### TaxRate

`TaxRate` is a reference/configuration entity.

Owns:

- Service or SAC classification
- GST rate
- Effective date range
- Active state

Rules:

- Rates must be configurable.
- Rates must be effective dated.
- Do not hardcode GST rates in code.

### Invoice

`Invoice` is an aggregate root.

Owns:

- Invoice number
- Status
- Financial totals
- GST snapshots
- Billing snapshots
- Invoice line items
- Issue and due dates

References:

- `organization_id`
- `branch_id`
- `family_id`
- `booking_id`
- optional source document metadata

Does not own:

- Family profile data as mutable references
- Booking fulfillment state
- Gallery selection state
- Delivery state

### Payment

`Payment` is an aggregate root.

Owns:

- Payment number
- Amount
- Method
- Status
- Transaction reference
- Received date
- Refund state

References:

- `invoice_id`
- `organization_id`
- `branch_id`

Completed payments update Invoice balances transactionally.

### CreditNote

`CreditNote` is an aggregate root or Invoice-owned adjustment aggregate. For
GST and accounting clarity, it should be a first-class Finance document.

Owns:

- Credit note number
- Original invoice reference
- Reason
- Line item adjustments
- Tax adjustment snapshots
- Status

### DebitNote

`DebitNote` is an aggregate root or Invoice-owned adjustment aggregate. For
GST and accounting clarity, it should be a first-class Finance document.

Owns:

- Debit note number
- Original invoice reference
- Reason
- Additional charge lines
- Tax adjustment snapshots
- Status

## Core Invariants

Invoice:

- Invoice numbers are sequence-backed.
- No `count() + 1` numbering.
- Draft invoices may be edited.
- Issued invoices should be immutable except status transitions and allowed
  notes.
- Invoice totals are immutable after a payment, credit note, or debit note
  exists.
- Void invoices cannot receive payments.
- Paid invoices cannot be edited.
- Balance due must never be negative.

Payment:

- Payment numbers are sequence-backed.
- Completed payment cannot overpay an invoice.
- Payments cannot be created for void invoices.
- Refunds must not exceed completed payment amount.
- Completed payment must update invoice amount paid and balance due in the
  same transaction.

Credit notes:

- Must reference an issued invoice.
- Must not exceed eligible invoice balance or paid amount without explicit
  refund policy.
- Must store tax snapshot adjustments.

Debit notes:

- Must reference an issued invoice.
- Must store tax snapshot additions.
- Must update invoice receivable state or create a linked receivable.

## Domain Events

Audit-backed events:

- `finance.settings_updated`
- `invoice.created`
- `invoice.updated`
- `invoice.issued`
- `invoice.voided`
- `invoice.overdue_marked`
- `payment.created`
- `payment.completed`
- `payment.failed`
- `payment.refunded`
- `credit_note.created`
- `credit_note.issued`
- `debit_note.created`
- `debit_note.issued`

These should remain audit-backed events unless an outbox is explicitly added in
a later sprint.

## API Surface

Required:

```text
GET /api/v1/finance/settings
PATCH /api/v1/finance/settings

GET /api/v1/tax-rates
POST /api/v1/tax-rates
PATCH /api/v1/tax-rates/{id}

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

GET /api/v1/credit-notes
POST /api/v1/credit-notes
GET /api/v1/credit-notes/{id}
POST /api/v1/credit-notes/{id}/issue

GET /api/v1/debit-notes
POST /api/v1/debit-notes
GET /api/v1/debit-notes/{id}
POST /api/v1/debit-notes/{id}/issue

GET /api/v1/finance/metrics
GET /api/v1/finance/tax-summary
GET /api/v1/finance/outstanding
GET /api/v1/finance/revenue
```

Optional workflow helpers:

```text
POST /api/v1/invoices/from-booking/{booking_id}
POST /api/v1/invoices/from-gallery-upgrade/{upgrade_request_id}
```

## Frontend Surface

Routes:

```text
/finance
/finance/invoices
/finance/invoices/:id
/finance/payments
/finance/payments/:id
/finance/credit-notes
/finance/debit-notes
/finance/reports/outstanding
/finance/reports/revenue
/finance/tax-summary
/finance/settings
```

Navigation:

```text
Finance
  Dashboard
  Invoices
  Payments
  Credit Notes
  Debit Notes
  Reports
  Settings
```

## Source References

- India Code, Central Goods and Services Tax Act, 2017:
  https://www.indiacode.nic.in/handle/123456789/15689
- CBIC GST goods and services rates:
  https://cbic-gst.gov.in/gst-goods-services-rates.html
- GST taxpayer search service:
  https://services.gst.gov.in/services/searchtp
