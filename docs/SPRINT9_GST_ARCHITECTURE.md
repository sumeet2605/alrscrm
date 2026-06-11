# Sprint 9 GST Architecture

Phase: architecture review only

No code, migrations, or runtime behavior were changed.

## Legal Reference Basis

This design is based on the current implementation and public GST references:

- India Code, Central Goods and Services Tax Act, 2017:
  https://www.indiacode.nic.in/handle/123456789/15689
- CBIC GST goods and services rates:
  https://cbic-gst.gov.in/gst-goods-services-rates.html
- GST taxpayer search service:
  https://services.gst.gov.in/services/searchtp

The CGST Act organizes GST concerns across registration, composition levy, tax
invoice, credit and debit notes, accounts, returns, payment, refunds, and audit.
The application should model enough data to support compliant invoices and
reports, but final compliance should be validated by a qualified tax advisor
before production use.

## GST Modes To Support

### Regular GST Registration

Tenant can collect GST and issue tax invoices.

Required support:

- GSTIN
- Legal name
- Trade name
- Principal billing address
- State code
- Place of supply
- GST rate by service/SAC
- CGST/SGST/IGST calculation
- Credit notes
- Debit notes
- GST returns summary

### Composition Scheme

Tenant may be under composition scheme.

Required support:

- Registration type marker.
- Invoice rendering rules that do not incorrectly show standard GST collection.
- Composition notes on invoice.
- Separate reporting classification.

### GST Exempt Business

Tenant may be exempt or operating below registration threshold.

Required support:

- Registration type marker.
- No GSTIN required.
- Invoice note for exemption/unregistered status.
- No CGST/SGST/IGST collection.

### Unregistered Business

Tenant may operate without GST registration.

Required support:

- Registration type marker.
- No GSTIN required.
- Invoice should not collect GST.
- Reports should separate non-GST revenue from taxable GST revenue.

## GST Concepts To Model

### Place Of Supply

Place of supply determines tax split:

- Same state: CGST + SGST.
- Different state: IGST.

Required fields:

- Supplier state code.
- Recipient state code.
- Place of supply state code.
- Supply type: `INTRA_STATE` or `INTER_STATE`.

### CGST, SGST, IGST

Invoice line items should snapshot:

- CGST rate
- CGST amount
- SGST rate
- SGST amount
- IGST rate
- IGST amount

Do not derive historical invoices from current tax rates.

### SAC Codes

Professional photography and related services should support SAC/HSN metadata.

Recommended:

- Store `sac_code` on TaxRate.
- Snapshot `sac_code` onto InvoiceLineItem.

### Reverse Charge

Reverse charge scenarios are uncommon for consumer studio invoices but should
be modeled as a flag.

Recommended fields:

- `reverse_charge_applicable`
- `reverse_charge_reason`

### Credit Notes

Credit notes reduce previously issued invoice value or tax.

Required:

- Original invoice reference.
- Reason.
- Tax adjustment snapshot.
- Line adjustment details.

### Debit Notes

Debit notes increase previously issued invoice value or tax.

Required:

- Original invoice reference.
- Reason.
- Tax adjustment snapshot.
- Line adjustment details.

## Recommended Schema

### `finance_settings`

Purpose:

- Tenant/branch finance identity and defaults.

Columns:

- `id`
- `organization_id`
- `branch_id nullable`
- `registration_type`
- `gstin nullable`
- `legal_name`
- `trade_name nullable`
- `billing_address`
- `billing_city`
- `billing_state`
- `billing_state_code`
- `billing_postal_code`
- `default_currency`
- `default_due_days`
- `invoice_prefix`
- `auto_create_booking_invoice`
- `require_payment_before_delivery`
- `created_at`
- `updated_at`

Constraints:

- Unique `(organization_id, branch_id)`.
- GSTIN required when registration type is `REGULAR` or `COMPOSITION`.
- GSTIN nullable when `EXEMPT` or `UNREGISTERED`.

### `tax_rates`

Purpose:

- Configurable, versioned GST rate table.

Columns:

- `id`
- `organization_id nullable`
- `service_type`
- `sac_code`
- `tax_rate`
- `description`
- `effective_from`
- `effective_to nullable`
- `is_active`
- `created_at`
- `updated_at`

Rules:

- Rates are effective dated.
- Tenant-specific override allowed through `organization_id`.
- Platform default rates use `organization_id = null`.
- No hardcoded percentages in service code.

### Invoice GST Snapshot

Invoice should store:

- Seller legal name
- Seller trade name
- Seller GSTIN
- Seller billing address
- Seller state code
- Buyer billing name
- Buyer GSTIN nullable
- Buyer billing address
- Buyer state code
- Place of supply state code
- Supply type
- GST registration type
- Reverse charge flag
- Taxable amount
- CGST amount
- SGST amount
- IGST amount
- Total tax amount

### Invoice Line Tax Snapshot

InvoiceLineItem should store:

- Description
- Service type
- SAC code
- Quantity
- Unit price
- Discount amount
- Taxable amount
- Tax rate
- CGST rate
- CGST amount
- SGST rate
- SGST amount
- IGST rate
- IGST amount
- Line total

## GSTIN Verification

### Option 1: Government GST Portal

Use:

- GST taxpayer search service.

Pros:

- Official source.
- No direct vendor dependency.

Cons:

- Public UI is not a stable production API.
- May block automated access.
- Legal and usage restrictions must be reviewed.
- Reliability is not guaranteed for application workflows.

Recommendation:

- Do not build automated production dependency on the public portal in Sprint 9.

### Option 2: GST Suvidha Provider

Pros:

- Designed for GST integrations.
- Better compliance posture.
- More reliable for production use.

Cons:

- Requires provider onboarding.
- Cost and contract review required.
- Implementation depends on provider API and auth model.

Recommendation:

- Best long-term direction for verified GST data.

### Option 3: Commercial GST APIs

Pros:

- Fastest integration.
- Often simple API contracts.
- Can return legal name, trade name, address, state, and status.

Cons:

- Paid.
- Vendor reliability varies.
- Data licensing and legal use must be reviewed.
- May still depend on government systems upstream.

Recommendation:

- Acceptable future option behind provider abstraction.

## Sprint 9 Recommendation

Sprint 9 should implement:

- Manual GSTIN entry.
- GSTIN format validation.
- Manual legal/trade name and address entry.
- Registration type support.
- Database-driven tax rates.
- Invoice tax snapshots.
- GST tax summary report.

Sprint 9 should not implement:

- Automated GSTIN lookup as a required workflow.
- GSP filing.
- GST return filing.
- E-invoicing.

## Future Recommendation

Sprint 9.2 or later:

- Add `gst_lookup_provider` abstraction.
- Integrate either GSP or commercial API.
- Store lookup snapshot:
  - GSTIN
  - legal name
  - trade name
  - address
  - state
  - status
  - provider
  - checked_at
  - raw response hash or reference

## Tax Reporting

Required Sprint 9 reports:

- Taxable sales by date range.
- CGST collected.
- SGST collected.
- IGST collected.
- Exempt/non-GST revenue.
- Credit note tax adjustments.
- Debit note tax adjustments.

Not required in Sprint 9:

- Direct GST return filing.
- GSTR form generation.
- Input tax credit accounting.
- Vendor purchase GST.

## Recommendation

```text
GO WITH CHANGES
```

GST support is feasible if Sprint 9 stores immutable invoice tax snapshots and
uses configurable effective-dated rates. Automated GSTIN lookup should be
deferred behind a provider abstraction.
