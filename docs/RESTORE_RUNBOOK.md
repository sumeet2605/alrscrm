# Restore Runbook

## Scope

This runbook covers ALRSCRM restore readiness for PostgreSQL and object storage.

## Restore Preconditions

- Incident declared.
- Target restore point approved.
- Database backup identifier selected.
- Storage restore point selected.
- Current deployment image recorded.
- Current Alembic version recorded.

## PostgreSQL Restore Process

1. Stop writes or isolate the impacted environment.
2. Create a new restore database from backup or PITR.
3. Confirm connectivity.
4. Check Alembic version:

```bash
alembic current
```

5. Run readiness check:

```bash
curl /health/ready
```

6. Run smoke tests for:
   - Login
   - Families
   - Bookings
   - Galleries
   - Delivery
   - Finance
   - Integrations

## Storage Restore Process

1. Identify impacted object prefix or bucket.
2. Restore object versions or replicated bucket.
3. Verify sample Gallery image access.
4. Verify sample Delivery artifact access.
5. Confirm signed URL generation.

## Application Rollback Process

1. Roll back backend and frontend together.
2. Do not run old frontend against incompatible backend contracts.
3. Do not downgrade database without a tested downgrade or restore plan.
4. Prefer restoring a snapshot over manual data repair for production
   corruption.

## Post-Restore Validation

- `/health/live` returns live.
- `/health/ready` returns ready.
- API structured logs include request IDs.
- Platform metrics endpoint responds to Super Admin.
- Audit logs continue recording request IDs.
- Tenant isolation smoke tests pass.

## Required Evidence Before Launch

- Restore drill completed in staging.
- Restore duration recorded.
- Data-loss window recorded.
- Runbook owner assigned.
