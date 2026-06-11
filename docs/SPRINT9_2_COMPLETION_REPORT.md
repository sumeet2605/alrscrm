# Sprint 9.2 Completion Report

Sprint 9.2 implements the Tenant Integrations Foundation and Finance PDF
hardening.

## Completed Scope

- `OrganizationIntegration` aggregate
- Tenant-owned encrypted integration credentials
- Integration provider status tracking
- Integration verification workflow
- Integration health dashboard API
- Settings > Integrations frontend navigation
- Integrations dashboard
- WhatsApp, Email, and Storage settings pages
- GST Invoice PDF endpoint
- Payment Receipt PDF endpoint
- RBAC seed updates
- Tenant and branch scoped integration tests
- OpenAPI TypeScript regeneration

## Supported Providers

- WhatsApp Cloud API
- Instagram Business
- Facebook Page
- SMTP Email
- Google Cloud Storage
- AWS S3

## Backend Files Created

- `backend/app/core/crypto.py`
- `backend/app/integrations/__init__.py`
- `backend/app/integrations/enums.py`
- `backend/app/integrations/models/__init__.py`
- `backend/app/integrations/models/integration.py`
- `backend/app/integrations/repositories.py`
- `backend/app/integrations/routes.py`
- `backend/app/integrations/schemas/__init__.py`
- `backend/app/integrations/schemas/integration.py`
- `backend/app/integrations/services/__init__.py`
- `backend/app/integrations/services/integration_service.py`
- `backend/app/finance/pdf.py`
- `backend/tests/test_integrations_api.py`

## Backend Files Updated

- `backend/.env.example`
- `backend/alembic/env.py`
- `backend/app/api/router.py`
- `backend/app/core/config.py`
- `backend/app/finance/routes.py`
- `backend/app/identity/seeds.py`
- `backend/tests/test_finance_api.py`

## Migration Created

- `backend/alembic/versions/202606100018_create_tenant_integrations.py`

Migration creates:

- `organization_integrations`

Indexes:

- `branch_id`
- `provider`
- `status`

Constraint:

- Unique provider per organization and branch scope.

## APIs Added

Integrations:

- `GET /api/v1/integrations`
- `GET /api/v1/integrations/health`
- `POST /api/v1/integrations`
- `PATCH /api/v1/integrations/{id}`
- `POST /api/v1/integrations/{id}/verify`

Finance PDFs:

- `GET /api/v1/invoices/{invoice_id}/pdf`
- `GET /api/v1/payments/{payment_id}/receipt`

## Security Notes

- Credentials are encrypted at rest.
- API responses expose only credential key names.
- Raw credential values are never returned by integration read APIs.
- Integration reads and writes are organization scoped.
- Branch-scoped users are restricted to their branch scope.
- Integration create, update, and verify actions write audit events.

New environment variable:

```text
INTEGRATION_ENCRYPTION_KEY
```

If omitted, local/development derives encryption key material from
`JWT_SECRET_KEY`. Production should set a dedicated value.

## RBAC Added

- `integrations:view`
- `integrations:manage`

Assigned to:

- Super Admin
- Organization Admin
- Owner
- Branch Manager

## Frontend Files Created

- `frontend/src/api/integrations.ts`
- `frontend/src/types/integrations.ts`
- `frontend/src/modules/settings/integrationOptions.ts`
- `frontend/src/modules/settings/IntegrationsDashboardPage.tsx`
- `frontend/src/modules/settings/IntegrationsDashboardPage.test.tsx`
- `frontend/src/modules/settings/IntegrationSettingsForm.tsx`
- `frontend/src/modules/settings/WhatsAppSettingsPage.tsx`
- `frontend/src/modules/settings/EmailSettingsPage.tsx`
- `frontend/src/modules/settings/StorageSettingsPage.tsx`

## Frontend Files Updated

- `frontend/src/api/finance.ts`
- `frontend/src/layouts/DashboardLayout.tsx`
- `frontend/src/routes/AppRoutes.tsx`
- `frontend/src/routes/routePermissions.ts`
- `frontend/src/routes/routePermissions.test.ts`
- `frontend/src/modules/finance/InvoiceDetailPage.tsx`
- `frontend/src/modules/finance/PaymentDetailPage.tsx`
- `frontend/src/types/generated/openapi-schema.json`
- `frontend/src/types/generated/openapi.ts`

## Frontend Routes Added

- `/settings/integrations`
- `/settings/integrations/whatsapp`
- `/settings/integrations/email`
- `/settings/integrations/storage`

Navigation added:

```text
Settings
  Integrations
```

## Explicit Non-Goals Preserved

Sprint 9.2 does not implement:

- WhatsApp messaging
- Instagram automation
- Credit Notes
- Debit Notes
- Accounting Ledger
- Platform Billing

## Verification Status

Completed:

```text
ruff check backend frontend: passed
ruff format --check backend frontend: passed
python -m pytest backend/tests: passed, 64 tests
npm run lint: passed
npm run test: passed, 37 tests
npm run build: passed
npm run generate:api-types: passed
docker compose up -d --build: passed
docker compose exec api alembic upgrade head: passed
```

Non-blocking warnings observed:

- Existing frontend Ant Design `act(...)` warning.
- Existing frontend dynamic/static Gallery API import warning.
- Existing frontend bundle-size warning.
- Existing backend datetime deprecation warnings in Gallery selection tests.
- Docker compose warning for unset local `BOOTSTRAP_ADMIN_PASSWORD`.

## Sprint 9.2 Status

Sprint 9.2 is implemented and verified for release review.
