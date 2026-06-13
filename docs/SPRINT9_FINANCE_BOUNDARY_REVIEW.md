# Sprint 9 Finance Boundary Review

Phase: architecture review only

No code, migrations, or runtime behavior were changed.

## Boundary Decision

Finance must be a separate bounded context.

Finance owns:

- Invoice lifecycle
- Invoice line items
- Receivables
- Payments
- Refunds
- Credit notes
- Debit notes
- GST snapshots
- Revenue reporting
- Tax reporting

Finance does not own:

- Booking fulfillment
- Gallery selection
- Editing production workflow
- Delivery lifecycle
- Family customer profile
- Sales pipeline forecasting

## Current Financial Fields And Ownership

| Domain | Entity | Field | Current Purpose | Future Owner |
| --- | --- | --- | --- | --- |
| Organization | OrganizationSettings | `currency` | Tenant currency default | FinanceSettings can override or reuse |
| Sales | Opportunity | `estimated_value` | Sales forecast | Sales remains owner |
| Booking | Package | `price` | Catalog list price | Booking catalog remains owner |
| Booking | PackageAddon | `price` | Catalog addon price | Booking catalog remains owner |
| Booking | Booking | `total_amount` | Booking order total | Booking snapshot, Invoice is finance truth |
| Booking | Booking | `advance_received` | Advance amount captured at booking | Legacy snapshot, Payment is finance truth |
| Booking | Booking | `balance_amount` | Remaining booking amount | Legacy snapshot, Invoice balance is finance truth |
| Booking | BookingItem | `price` | Snapshotted package price | Booking remains owner |
| Booking | BookingItem | `discount` | Snapshotted discount | Booking remains owner, copied to Invoice |
| Booking | BookingItem | `final_amount` | Snapshotted item total | Booking remains owner, copied to Invoice |
| Booking | BookingItemAddon | `price` | Snapshotted addon price | Booking remains owner |
| Gallery | GalleryUpgradeRequest | `price_per_photo` | Upgrade quote | Gallery quote, Invoice line bills it |
| Gallery | GalleryUpgradeRequest | `total_amount` | Upgrade quote total | Gallery quote, Invoice line bills it |
| Gallery | GalleryUpgradeRequest | `status = PAID` | Payment marker | Deprecated from finance truth |
| Delivery | DeliveryJob | `re_download_fee` | Re-download policy price | Delivery policy, Finance bills it |
| Delivery | Metrics | `revenue_potential` | Potential future revenue | Finance reporting should replace |

## What Should Remain In Existing Aggregates

### Booking

Keep:

- Package and addon catalog prices.
- Booking item price snapshots.
- Booking item discounts.
- Booking total snapshot.
- Existing `advance_received` and `balance_amount` for backward compatibility.

Reason:

- Booking already acts as the fulfillment/order source.
- Existing APIs and frontend pages display these fields.
- Removing them would break backward compatibility.

Do not add:

- Invoice status.
- Payment status.
- Refund status.
- GST status.
- Credit/debit note state.

### Gallery

Keep:

- Upgrade request quantity and requested selection limit.
- Upgrade quote amount for operational review.

Deprecate as financial truth:

- `GalleryUpgradeRequest.status = PAID`

Reason:

- Gallery is selection workflow, not receivables.
- Paid/unpaid state must move to Invoice/Payment.

### Delivery

Keep:

- `allow_re_download`
- `re_download_fee`

Reason:

- These fields define delivery policy.

Do not add:

- Payment status.
- Invoice status.
- Transaction references.
- GST data.

Delivery release should query Finance when payment enforcement is enabled.

## What Must Move Into Finance

Move or replace as source of truth:

- Booking balance truth moves to Invoice.
- Booking advance truth moves to Payment.
- Gallery upgrade payment truth moves to Invoice/Payment.
- Delivery re-download billing truth moves to Invoice/Payment.
- Revenue metrics move to Finance.
- Tax summaries move to Finance.

## Aggregate Boundaries

### Invoice Aggregate

Root:

- `Invoice`

Children:

- `InvoiceLineItem`

References:

- `organization_id`
- `branch_id`
- `family_id`
- `booking_id`
- optional source document metadata

Invariants:

- Invoice number is sequence-backed.
- Draft can be edited.
- Issued invoice becomes immutable except allowed status transitions.
- Payment locks invoice financial totals.
- Void invoice cannot receive payment.
- Balance due cannot be negative.

### Payment Aggregate

Root:

- `Payment`

References:

- `invoice_id`
- `organization_id`
- `branch_id`
- `received_by_user_id`

Invariants:

- Payment number is sequence-backed.
- Completed payment cannot overpay invoice.
- Completed payment updates invoice balances transactionally.
- Refund cannot exceed completed payment amount.

### CreditNote Aggregate

Root:

- `CreditNote`

References:

- Original invoice.
- Organization and branch.

Invariants:

- Must reference an issued invoice.
- Must store reason and tax adjustment snapshot.
- Must not create negative receivable.

### DebitNote Aggregate

Root:

- `DebitNote`

References:

- Original invoice.
- Organization and branch.

Invariants:

- Must reference an issued invoice.
- Must store reason and tax adjustment snapshot.
- Must increase receivable or create a linked receivable.

## Cross-Domain Integration

### Booking To Invoice

Recommended flow:

```text
Booking CONFIRMED
  -> optional draft Invoice
  -> Invoice line items copied from BookingItem snapshots
```

Do not:

- Mutate Booking payment state from Finance by default.
- Require every historical Booking to have an Invoice.

### Gallery Upgrade To Invoice

Recommended flow:

```text
GalleryUpgradeRequest APPROVED
  -> create Invoice or append InvoiceLineItem
  -> Payment collected in Finance
  -> Gallery may read Finance status for display
```

Do not:

- Mark Gallery upgrade as paid from Gallery service as financial truth.

### Delivery To Finance

Recommended flow:

```text
Delivery send requested
  -> Finance checks outstanding invoices
  -> Delivery SENT allowed only if balance due is zero when enforcement is on
```

Do not:

- Store payment status in DeliveryJob.

## Boundary Decision Summary

| Question | Decision |
| --- | --- |
| Should Booking continue storing `advance_received`? | Yes, as compatibility snapshot only. |
| Should Booking continue storing `balance_amount`? | Yes, as compatibility snapshot only. |
| Should Finance derive true receivables? | Yes. |
| Should Gallery upgrade requests store payment status? | Not as truth. Treat `PAID` as legacy/operational. |
| Should Delivery store re-download fee? | Yes, as policy price only. |
| Should Delivery own payment status? | No. |

## Required Architecture Decisions

Before implementation, confirm:

1. Historical Booking advances will not automatically create payments unless
   explicitly requested.
2. Gallery `mark-paid` remains legacy or is replaced by Finance workflows.
3. Delivery payment enforcement checks all non-void invoices for the booking.
4. Partial payment allocation for service-type revenue is deferred or defined.
5. Credit notes and debit notes are first-class Finance documents.

## Recommendation

```text
GO WITH CHANGES
```

Finance can proceed only if it is treated as the source of truth for financial
state and existing monetary fields are treated as snapshots, policies, or
operational quotes.
