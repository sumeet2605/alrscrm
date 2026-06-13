# Sprint 9.4 Disaster Recovery Plan

## Objective

Define the restore path for ALRSCRM production assets.

Sprint 9.4 documents disaster recovery and adds readiness hooks. It does not
automate cloud backups or restores.

## Critical Assets

- PostgreSQL database
- Object storage
- Deployment configuration
- Secrets
- Audit logs
- Finance documents

## Recovery Objectives

Pilot recommendation:

| Objective | Target |
| --- | --- |
| RPO | 24 hours maximum until PITR is enabled |
| RTO | 4-8 hours for pilot |
| Restore drill | Required before pilot launch |

Full production recommendation:

| Objective | Target |
| --- | --- |
| RPO | 15 minutes or PITR-backed |
| RTO | 1-2 hours |
| Restore drill | Quarterly |

## Restore Order

1. Freeze writes or isolate impacted environment.
2. Restore PostgreSQL snapshot or PITR target.
3. Restore object storage bucket or versioned objects.
4. Run Alembic version compatibility check.
5. Start backend with `/health/ready` validation.
6. Smoke test tenant login, Gallery, Delivery, Finance, and Integrations.
7. Review audit logs for incident window.

## Rollback Strategy

- Roll back application image and frontend bundle together.
- Do not run old frontend against incompatible API contracts.
- Do not downgrade database without an explicit migration rollback and backup.
- Prefer restore from backup over destructive manual repair for production
  corruption.

## Remaining Gaps

- Automated backup provider.
- Restore automation scripts.
- Tenant-level recovery tools.
- DR environment.
- DR alerting.
