# Sprint 9 Estimation

Phase: architecture review only

No code, migrations, or runtime behavior were changed.

## Summary

Recommended delivery:

- Sprint 9.1: Core Finance
- Sprint 9.2: Compliance and integrations

Total estimate:

```text
12-18 engineering days
```

This assumes one senior full-stack engineer with existing repo context. With
parallel backend/frontend ownership, calendar time can be reduced.

## Sprint 9.1 Estimate

Goal:

- Core tenant Finance for invoices, payments, settings, and basic reporting.

| Workstream | Estimate |
| --- | --- |
| Backend Finance module structure | 0.5 day |
| Finance settings model/API | 1 day |
| TaxRate model/API | 1 day |
| Invoice model/schema/repository/service/routes | 2 days |
| Invoice sequence and migration | 0.5 day |
| Invoice line item calculation and snapshots | 1 day |
| Payment model/schema/repository/service/routes | 1.5 days |
| Payment sequence and transactional balance updates | 1 day |
| RBAC seeds and route permissions | 0.5 day |
| Audit events | 0.5 day |
| Metrics API | 1 day |
| Backend tests | 2 days |
| Frontend Finance navigation/routes | 0.5 day |
| Finance Dashboard | 1 day |
| Invoice List and Detail | 1.5 days |
| Payment List and Detail | 1 day |
| Finance Settings | 1 day |
| Frontend tests | 1 day |
| OpenAPI generation and verification | 0.5 day |

Sprint 9.1 total:

```text
16-18 engineering days
```

Minimum viable Sprint 9.1 if scope is reduced:

```text
9-12 engineering days
```

Reduced scope would defer TaxRate admin UI, advanced metrics, and some reports.

## Sprint 9.2 Estimate

Goal:

- Compliance, adjustments, delivery gate, upgrade billing, PDFs, and reports.

| Workstream | Estimate |
| --- | --- |
| CreditNote backend | 1.5 days |
| DebitNote backend | 1.5 days |
| Credit/Debit note frontend | 1.5 days |
| GST tax summary API | 1 day |
| Outstanding report | 1 day |
| Revenue report | 1 day |
| Revenue by service type | 1 day |
| Delivery payment gate | 1 day |
| Gallery upgrade invoice workflow | 1 day |
| Invoice PDF generation | 2 days |
| Invoice template decision/UI | 1-2 days |
| Additional backend tests | 2 days |
| Additional frontend tests | 1 day |
| Full verification | 0.5 day |

Sprint 9.2 total:

```text
15-18 engineering days
```

## Recommended Sprint Breakdown

### Sprint 9.1: Core Finance

Deliver:

- FinanceSettings
- TaxRate
- Invoice
- InvoiceLineItem
- Payment
- Finance Dashboard
- Invoice pages
- Payment pages
- Basic metrics
- Tenant and branch tests

Do not deliver:

- Credit notes
- Debit notes
- PDF generation
- Delivery release gate
- GSTIN API lookup
- Platform finance

### Sprint 9.2: Finance Compliance And Integration

Deliver:

- Credit notes
- Debit notes
- GST tax summary
- Invoice PDFs
- Gallery upgrade billing
- Delivery payment gate
- Outstanding report
- Revenue report

Do not deliver:

- Razorpay
- Stripe
- Accounting exports
- GST filing
- Platform subscription billing

## Staffing Recommendation

Preferred:

- 1 backend lead
- 1 frontend lead
- 1 QA/reviewer part-time

Minimum:

- 1 senior full-stack engineer

## Risk Buffer

Add 25-35% buffer because Finance includes:

- Money calculations
- Tenant isolation
- GST snapshots
- Concurrent payment safety
- Reporting accuracy

## Final Estimate

```text
Sprint 9.1: 9-18 engineering days depending on scope.
Sprint 9.2: 15-18 engineering days.
Full Finance foundation: 24-36 engineering days.
```

Recommendation:

```text
Do not compress all Finance scope into one sprint.
```
