# Sprint 9 Implementation Plan

Phase: architecture review only

No code, migrations, or runtime behavior were changed.

## GO / NO-GO

Recommendation:

```text
GO WITH CHANGES
```

Sprint 9 can begin after the Finance boundary, GST, and platform finance
decisions are accepted.

## Required Architecture Decisions

Before implementation:

1. Finance becomes the source of truth for invoices, payments, receivables,
   credit notes, debit notes, GST snapshots, and revenue reporting.
2. Booking monetary fields remain backward-compatible snapshots.
3. Gallery upgrade payment status is deprecated from financial truth.
4. Delivery re-download fee remains policy state only.
5. Delivery payment gating reads Finance state.
6. GST rates are configurable, versioned, and effective dated.
7. GSTIN lookup is manual in Sprint 9 and provider-based later.
8. Platform finance is separate from tenant finance.

## Sprint 9.1 Recommended Scope

Goal:

- Establish Finance core for tenant studio invoices and payments.

Backend:

- Add Finance module structure.
- Add enums:
  - InvoiceStatus
  - PaymentStatus
  - PaymentMethod
  - CreditNoteStatus
  - DebitNoteStatus
  - GSTRegistrationType
  - SupplyType
- Add models:
  - FinanceSettings
  - TaxRate
  - Invoice
  - InvoiceLineItem
  - Payment
- Add sequence-backed invoice numbers.
- Add sequence-backed payment numbers.
- Add services and repositories.
- Add audit events.
- Add RBAC permissions.
- Add API routes for settings, tax rates, invoices, payments, metrics.
- Add tenant and branch scoped tests.

Frontend:

- Add Finance navigation.
- Add Finance Dashboard.
- Add Invoice List.
- Add Invoice Detail.
- Add Payment List.
- Add Payment Detail.
- Add Finance Settings.
- Add route permission tests.

Reports:

- Revenue this month.
- Revenue this year.
- Outstanding amount.
- Paid amount.
- Overdue amount.
- Invoices by status.
- Payments by method.

Out of scope for Sprint 9.1:

- Credit notes.
- Debit notes.
- Platform finance.
- GSTIN provider integration.
- Direct GST return filing.
- Accounting exports.

## Sprint 9.2 Recommended Scope

Goal:

- Complete compliance and adjustment workflows.

Backend:

- Add CreditNote aggregate.
- Add DebitNote aggregate.
- Add GST tax summary API.
- Add invoice PDF generation support.
- Add invoice template model if needed.
- Add Gallery upgrade to Invoice workflow.
- Add Delivery payment gate.
- Add revenue by service type.
- Add branch revenue.
- Add average collection time.
- Add GST lookup provider abstraction, without binding to a specific vendor.

Frontend:

- Add Credit Note pages.
- Add Debit Note pages.
- Add Outstanding Report.
- Add Revenue Report.
- Add Tax Summary Report.
- Add Gallery upgrade billing actions.
- Add Delivery blocked-by-payment UI state.
- Add invoice PDF download.

Out of scope for Sprint 9.2:

- Platform subscription billing.
- Razorpay.
- Stripe.
- Full accounting ledger.
- Bank reconciliation.
- GST filing.
- Income tax return filing.

## Backend Implementation Order

1. Add finance enums and schemas.
2. Add models and Alembic migration.
3. Add repository with scoped query helpers.
4. Add service invariants.
5. Add routes.
6. Add RBAC seeds.
7. Add audit events.
8. Add tests.
9. Wire API router.
10. Regenerate frontend OpenAPI types.

## Frontend Implementation Order

1. Add finance API adapter.
2. Add finance types from generated OpenAPI where possible.
3. Add route permissions.
4. Add navigation.
5. Add dashboard.
6. Add invoice workflows.
7. Add payment workflows.
8. Add settings pages.
9. Add frontend tests.

## Required Backend Tests

- Cross-tenant invoice access denied.
- Cross-branch invoice access denied.
- Cross-tenant payment access denied.
- Cross-branch payment access denied.
- Invoice number sequence generation.
- Payment number sequence generation.
- Payment cannot overpay invoice.
- Payment cannot be made against void invoice.
- Completed payment updates invoice balances.
- Invoice totals immutable after payment.
- Tax rates are effective dated.
- GST snapshots persist after rate change.
- Finance metrics are tenant scoped.
- Finance metrics are branch scoped.

## Required Frontend Tests

- Finance navigation visible to Super Admin, Owner, Organization Admin, Branch
  Manager.
- Finance navigation hidden from Photographer and Editor.
- Invoice list renders.
- Invoice creation workflow.
- Payment creation workflow.
- Finance settings workflow.
- Protected finance route redirects unauthorized users.

## Verification Commands

Run after implementation:

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

## Release Criteria

Sprint 9 can be marked complete only when:

- Finance is a separate bounded context.
- No new financial lifecycle state is added to Booking, Gallery, Editing, or
  Delivery.
- Invoice and Payment are source of truth.
- Tenant and branch isolation tests pass.
- GST snapshots are stored.
- Tax rates are configurable and effective dated.
- Audit events include tenant and branch scope.
- Frontend routes and RBAC are tested.

## Recommendation

```text
Proceed with Sprint 9.1 after architecture approval.
```
