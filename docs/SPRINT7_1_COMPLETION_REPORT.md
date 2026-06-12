# Sprint 7.1 Completion Report

Sprint 7.1 hardens Delivery Management for secure client delivery.

## Files Created

- `docs/SPRINT7_1_DELIVERY_HARDENING.md`
- `docs/DELIVERY_SECURITY_MODEL.md`
- `docs/DELIVERY_LIFECYCLE_STATE_MACHINE.md`
- `docs/SPRINT7_1_COMPLETION_REPORT.md`

## Files Modified

- `backend/alembic/versions/202606100014_harden_delivery_security.py`
- `backend/app/delivery/models/__init__.py`
- `backend/app/delivery/models/delivery.py`
- `backend/app/delivery/repositories.py`
- `backend/app/delivery/routes.py`
- `backend/app/delivery/schemas/__init__.py`
- `backend/app/delivery/schemas/delivery.py`
- `backend/app/delivery/services/delivery_service.py`
- `backend/tests/test_delivery_api.py`
- `frontend/src/api/delivery.ts`
- `frontend/src/api/http.ts`
- `frontend/src/modules/delivery/ClientDeliveryPage.tsx`
- `frontend/src/modules/delivery/ClientDeliveryPage.test.tsx`
- `frontend/src/modules/delivery/DeliveryDetailPage.tsx`
- `frontend/src/modules/delivery/DeliveryQueuePage.tsx`
- `frontend/src/modules/delivery/DeliveryQueuePage.test.tsx`
- `frontend/src/modules/delivery/deliveryOptions.ts`
- `frontend/src/routes/AppRoutes.tsx`
- `frontend/src/routes/routePermissions.ts`
- `frontend/src/routes/routePermissions.test.ts`
- `frontend/src/types/delivery.ts`

## Migration

- `202606100014_harden_delivery_security`

Migration changes:

- Creates `delivery_number_seq`.
- Adds `delivery_password_hash` to `delivery_jobs`.
- Adds `reopen_requested_at` to `delivery_jobs`.
- Adds tenant and branch columns to `delivery_audits`.
- Creates `delivery_access_tokens`.
- Creates `delivery_artifacts`.
- Creates `delivery_reopen_attempts`.

## APIs Added Or Changed

Added:

- `POST /api/v1/delivery/public/authenticate`
- `POST /api/v1/delivery/jobs/{job_id}/close`
- `POST /api/v1/delivery/jobs/{job_id}/access-token/rotate`
- `POST /api/v1/delivery/jobs/{job_id}/access-token/revoke`

Changed:

- Public delivery access now uses `/api/v1/delivery/client/{token}`.
- Public download now requires a delivery session bearer token.
- Public reopen requests now use `/api/v1/delivery/client/{token}/reopen-request`.
- Delivery update payload no longer accepts lifecycle status fields.

## Security Improvements

- Opaque tokenized public delivery links.
- Hashed token storage.
- Token expiry, revocation, and rotation.
- Optional bcrypt-protected delivery passwords.
- Temporary 24-hour public delivery session tokens.
- Signed artifact download URLs.
- Reopen request cooldown and IP rate limit.
- Tenant and branch audit columns.

## Verification Status

Completed during implementation:

```text
python -m pytest backend/tests/test_delivery_api.py: 9 passed
ruff check backend frontend: passed
ruff format --check backend frontend: passed
python -m pytest backend/tests: 48 passed
npm run lint: passed
npm run test: 29 passed
npm run build: passed
npm run generate:api-types: passed
docker compose up -d --build: passed
docker compose exec api alembic upgrade head: passed
```

Non-blocking warnings observed:

- Existing frontend Ant Design `act(...)` warning in `DashboardLayout.test.tsx`.
- Existing frontend bundle-size warning.
- Existing backend datetime deprecation warnings in gallery selection tests.

## Remaining Debt

- ZIP generation currently creates the delivery artifact through the existing
  storage abstraction. Future work can expand artifact creation to package
  individual final image binaries when the storage abstraction exposes source
  object reads.
- Public delivery emails or messaging are not implemented in Sprint 7.1.
- Event delivery remains audit-backed; no outbox or event bus was introduced.
