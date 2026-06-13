# Backup Runbook

## Scope

This runbook covers ALRSCRM production backup readiness.

Sprint 9.4 creates the backup configuration framework but does not automate
cloud backups.

## Backup Assets

- PostgreSQL database
- Object storage bucket
- Environment and deployment secrets
- Alembic migration history
- Audit logs
- Finance documents

## PostgreSQL Backup Procedure

1. Confirm production database identifier.
2. Confirm the current Alembic version:

```bash
docker compose exec api alembic current
```

3. Trigger managed database backup or logical backup according to the provider.
4. Record backup identifier, timestamp, and Alembic version.
5. Verify backup completion.
6. Store backup metadata in the operations log.

## Object Storage Backup Procedure

1. Confirm production bucket name.
2. Confirm bucket versioning or replication status.
3. Confirm lifecycle policy.
4. Verify sample Gallery image and Delivery artifact are recoverable.
5. Record verification timestamp.

## Backup Frequency

Pilot:

- Database: daily
- Storage: versioned or daily replication
- Retention: 30 days

Production:

- Database: PITR plus daily snapshot
- Storage: versioned/replicated
- Retention: policy driven

## Backup Configuration

The application stores backup readiness configuration:

- `backup_enabled`
- `backup_frequency`
- `retention_days`
- `last_backup_at`

This table is a control-plane record. It is not the backup executor.

## Failure Handling

If backup fails:

1. Mark incident severity.
2. Stop non-critical deployments.
3. Retry backup.
4. Escalate if backup cannot be completed within RPO.

## Required Evidence Before Launch

- Last successful database backup.
- Last successful storage backup or replication verification.
- Last successful restore drill.
- Approved RPO and RTO.
