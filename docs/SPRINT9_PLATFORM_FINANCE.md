# Sprint 9 Platform Finance

Phase: architecture review only

No code, migrations, or runtime behavior were changed.

## Decision

Tenant finance and ALRSCRM platform finance must be separate.

Tenant finance is for studio operations:

- Customer invoices
- Customer payments
- Studio receivables
- Studio GST settings
- Studio revenue reports

Platform finance is for ALRSCRM SaaS operations:

- Tenant subscriptions
- Storage charges
- WhatsApp markup billing
- AI usage billing
- Add-on purchases
- Platform invoices to tenants

## Current Constraint

The current implementation still models Super Admin inside the `ALRSCRM`
pseudo-organization. See:

- `docs/PLATFORM_VS_TENANT_ARCHITECTURE_REVIEW.md`

That architecture is transitional. Finance should not rely on `ALRSCRM` as a
normal tenant organization.

## Recommended Separation

### Tenant Finance Bounded Context

Purpose:

- Finance for each photography studio tenant.

Scope:

- `organization_id` required.
- `branch_id` required where operationally relevant.

Tables:

- `finance_settings`
- `tax_rates`
- `invoices`
- `invoice_line_items`
- `payments`
- `credit_notes`
- `debit_notes`

### Platform Finance Bounded Context

Purpose:

- Finance for the ALRSCRM SaaS business.

Scope:

- Platform customer is the tenant organization.
- Platform invoice bills a tenant organization, not a family/customer.

Recommended future tables:

- `platform_customers`
- `platform_subscriptions`
- `platform_subscription_items`
- `platform_invoices`
- `platform_invoice_line_items`
- `platform_payments`
- `platform_usage_charges`
- `platform_credit_notes`
- `platform_debit_notes`

## Separate Tables Vs Shared Tables

### Recommended For Sprint 9

Use separate tenant finance tables only.

Reason:

- Sprint 9 is about studio/customer finance.
- Platform subscriptions and SaaS billing are not in scope.
- Current platform identity separation is not complete.

### Recommended Future Platform Finance

Use separate platform finance tables or a separate schema.

Preferred:

```text
Same database, shared schema, separate platform finance tables
```

Reason:

- Consistent with current shared database/shared schema architecture.
- Avoids cross-contaminating tenant customer invoices with ALRSCRM platform
  invoices.
- Easier migration than separate database.

Not recommended now:

```text
Same tables with nullable family_id/booking_id and tenant-as-customer rows
```

Reason:

- Blurs tenant finance and platform finance.
- Increases cross-tenant reporting risk.
- Forces many nullable domain references.

Separate database is not required at current scale.

## Tenant Finance Model

Tenant Finance:

```text
Organization
└── Branch
    ├── Family
    ├── Booking
    ├── Invoice
    ├── Payment
    ├── CreditNote
    └── DebitNote
```

Tenant finance rules:

- Tenant users see only their own organization finance.
- Branch Manager sees only branch finance.
- Super Admin may access tenant finance only through explicit platform
  authority.
- Public client routes do not expose tenant finance.

## Platform Finance Model

Platform Finance:

```text
Platform
└── Tenant Organization as customer
    ├── Subscription
    ├── Usage charges
    ├── Platform invoice
    └── Platform payment
```

Platform finance rules:

- Platform finance is not visible to tenant users.
- Tenant Owner may later view subscription invoices through a separate billing
  portal, not through studio Finance.
- Platform invoices do not reference Family or Booking.
- Platform finance events are platform audit events.

## Platform Charges

Future charge types:

- Base subscription fee.
- Per-branch fee.
- User seat fee.
- DigitalOcean storage pass-through or markup.
- WhatsApp messaging markup.
- AI edit or analysis usage.
- Premium support.
- Add-on modules.

These should not be mixed with studio revenue reports.

## Reporting Separation

Tenant reports:

- Revenue by booking.
- Revenue by service type.
- Outstanding customer invoices.
- GST summary.
- Branch revenue.

Platform reports:

- MRR/ARR.
- Tenant subscription status.
- Usage revenue.
- Platform receivables.
- Churn risk.
- Platform tax output.

## Recommendation

```text
Sprint 9: implement tenant Finance only.
Future sprint: implement Platform Finance as a separate bounded context.
```

Do not bill ALRSCRM subscriptions through tenant Invoice and Payment tables in
Sprint 9.
