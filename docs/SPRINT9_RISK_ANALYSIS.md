# Sprint 9 Risk Analysis

Phase: architecture review only

No code, migrations, or runtime behavior were changed.

## Final Recommendation

```text
GO WITH CHANGES
```

Finance is feasible, but it is a high-risk domain because it touches money,
tax, tenant isolation, reporting, and delivery release.

## Risk Register

| Risk | Severity | Impact | Mitigation |
| --- | --- | --- | --- |
| Booking monetary fields conflict with Finance truth | High | Incorrect balances and duplicate truth | Treat Booking values as snapshots only. |
| Gallery upgrade `PAID` conflicts with Payment | High | Upgrade billing becomes inconsistent | Deprecate as financial truth and use Invoice/Payment. |
| Delivery stores payment state | High | Delivery becomes finance owner | Only query Finance for release gate. |
| GST rates hardcoded | Critical | Incorrect tax after rate changes | Use versioned effective-dated TaxRate records. |
| Missing GST snapshots | Critical | Historical invoices change when settings change | Store full invoice and line tax snapshots. |
| Cross-tenant finance leak | Critical | Tenant data breach | Enforce organization and branch filters in every query. |
| Platform finance mixed with tenant finance | High | Bad SaaS reporting and data leakage | Keep platform finance separate. |
| Overpayment accepted | High | Incorrect receivables and refunds | Transactional payment validation. |
| Invoice edited after payment | High | Audit and accounting inconsistency | Lock financial totals after payment. |
| Credit/debit notes omitted | Medium | GST and adjustment workflows incomplete | Add in Sprint 9.2 at latest. |
| GSTIN lookup uses unofficial endpoint | Medium | Reliability/legal risk | Manual entry in Sprint 9, provider abstraction later. |
| Partial payment revenue allocation unclear | Medium | Wrong revenue by service type | Defer or define allocation rule. |
| Invoice PDF not immutable | Medium | Disputes over invoice content | Store snapshots and generated PDF metadata. |
| Reporting based on Booking totals | Medium | Revenue overstatement | Report from completed payments and invoices. |
| Platform Super Admin pseudo-tenant confusion | Medium | ALRSCRM appears as tenant finance | Do not create tenant finance for ALRSCRM by default. |

## Blockers

Implementation should not start until these are decided:

1. Booking monetary fields are compatibility snapshots.
2. Finance owns true receivables and payments.
3. Gallery upgrade payment marker is deprecated from financial truth.
4. Delivery payment gate reads Finance state.
5. GST rates are database-driven and effective dated.
6. Credit and debit note architecture is accepted.
7. Platform finance is out of Sprint 9 tenant finance scope.

## Security Risks

### Tenant Isolation

Finance data is highly sensitive. Every finance row must include:

- `organization_id`
- `branch_id`

Every repository query must apply:

- organization scope
- branch scope for branch-scoped users

### Public Routes

Public Gallery and Delivery routes must not expose:

- invoices
- payments
- balances
- tax data
- customer financial history

### Audit

Every finance mutation must write audit events with:

- `organization_id`
- `branch_id`
- actor user
- target type
- target id
- domain event metadata

## Compliance Risks

GST support is not only calculation. It requires:

- seller GST snapshot
- buyer billing snapshot
- place of supply
- SAC code
- CGST/SGST/IGST split
- credit notes
- debit notes
- invoice immutability

Do not present Sprint 9 as full GST filing compliance. It should support GST
invoice and tax summary data, not return filing.

## Data Migration Risks

Existing data has:

- Booking advances.
- Booking balances.
- Gallery upgrade paid markers.
- Delivery re-download fee policy.

Do not automatically migrate all historical values into Finance unless a
business reconciliation process is defined.

Recommended:

- New Finance records only for new workflows.
- Optional manual invoice creation from existing bookings.
- Optional admin-assisted migration later.

## Operational Risks

- Invoice numbering must be sequence-backed.
- Payment creation must be transactional.
- Concurrent payments must lock invoice rows or otherwise prevent overpayment.
- Rate changes must not affect historical invoices.
- Finance reports must handle voided invoices and refunds correctly.

## Risk Mitigation Plan

Sprint 9.1:

- Implement only core Invoice and Payment.
- Add strong tenant tests.
- Add sequence-backed numbering.
- Add immutable invoice snapshots.
- Add database constraints for non-negative amounts.

Sprint 9.2:

- Add credit/debit notes.
- Add delivery release gate.
- Add upgrade billing workflow.
- Add tax summary reports.
- Add invoice PDF generation.

## Release Gate

Do not release Sprint 9 unless:

- Full backend test suite passes.
- Frontend tests pass.
- Migration upgrade passes on PostgreSQL.
- Cross-tenant finance tests pass.
- Overpayment tests pass.
- Invoice immutability tests pass.
- GST snapshot tests pass.

## Recommendation

```text
GO WITH CHANGES
```

The Finance domain should proceed only with strict bounded context separation
and tenant-safe reporting.
