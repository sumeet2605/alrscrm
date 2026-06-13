# Sprint 8 Test Strategy

## Backend Tests

Added or updated coverage:

- Organization onboarding creates Organization, Settings, Branch, Owner, and
  Owner role assignment.
- Duplicate organization code is rejected.
- Failed duplicate onboarding does not create extra child records.
- Organization settings can be updated.
- Non-platform users cannot onboard organizations.
- Platform bootstrap is idempotent.
- Sample tenant is not created by default.
- Sample tenant is created only when `SEED_SAMPLE_TENANT=true`.

## Frontend Tests

Added coverage:

- Organization list renders data from API.
- Organization list navigates to onboarding.
- Organization onboarding wizard validates and submits expected payload.
- Route permissions allow `/organizations` only for Super Admin.

## Full Verification Commands

```bash
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

