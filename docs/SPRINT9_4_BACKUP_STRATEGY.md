# Sprint 9.4 Backup Strategy

Sprint 9.4 implements backup readiness framework only. It does not automate
cloud backups.

## Assets To Protect

- PostgreSQL database
- Object storage media and delivery artifacts
- Environment secrets
- Alembic migration history
- Audit logs
- Finance invoices and payment records

## PostgreSQL Backup Target

Required for production:

- Automated daily logical backup at minimum.
- Point-in-time recovery for production launch if using managed PostgreSQL.
- Backup encryption.
- Backup integrity check.
- Restore drill before pilot launch.

## Cloud Storage Backup Target

Required for production:

- Bucket versioning or replication.
- Lifecycle policy for old delivery artifacts.
- Retention policy for original Gallery images.
- Access log review.

## Backup Configuration Model

Sprint 9.4 adds a backup configuration model storing:

- `backup_enabled`
- `backup_frequency`
- `retention_days`
- `last_backup_at`

This is a readiness framework. It does not perform cloud backup automation.

## Recommended Frequencies

| Environment | Database Backup | Storage Backup | Retention |
| --- | --- | --- | --- |
| Staging | Daily | Daily/versioned | 7-14 days |
| Pilot production | Daily plus PITR | Versioned/replicated | 30-90 days |
| Full production | PITR plus daily snapshots | Versioned/replicated | Policy driven |

## Remaining Gaps

- Managed backup provider selection.
- Restore automation.
- Tenant-level export/restore strategy.
- Backup failure alerting.
- Backup encryption key rotation.

## Sprint 9.4 Deliverable

Sprint 9.4 creates the framework and runbook, then leaves actual automation for
the deployment platform implementation.
