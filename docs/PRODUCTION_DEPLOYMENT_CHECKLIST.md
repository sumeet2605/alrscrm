# Production Deployment Checklist

## Release Gate

ALRSCRM should not be opened for public SaaS traffic until this checklist is
complete or explicitly waived by the release owner.

## Cloud Run

- [ ] Container image built from reviewed commit.
- [ ] `APP_ENV` or `ENVIRONMENT` set to `production`.
- [ ] `/health/live` configured for liveness.
- [ ] `/health/ready` configured for readiness.
- [ ] Request timeout defined.
- [ ] Concurrency defined.
- [ ] Minimum and maximum instances defined.
- [ ] Structured logs routed to centralized logging.

## Cloud SQL

- [ ] PostgreSQL instance provisioned.
- [ ] Backups enabled.
- [ ] PITR enabled or launch waiver approved.
- [ ] Connection pool sizing reviewed.
- [ ] Migration runbook followed.
- [ ] Restore drill completed.

## Storage

- [ ] Private bucket configured.
- [ ] Signed URL access verified.
- [ ] CDN does not bypass private media controls.
- [ ] Lifecycle policy configured.
- [ ] Bucket backup, versioning, or replication configured.

## Redis

- [ ] Managed Redis provisioned.
- [ ] `REDIS_URL` configured.
- [ ] Redis health monitored.
- [ ] Login rate limiting tested.

## Secrets

- [ ] `SECRET_KEY` configured.
- [ ] `JWT_SECRET` or `JWT_SECRET_KEY` configured.
- [ ] `INTEGRATION_ENCRYPTION_KEY` configured.
- [ ] Database credentials configured.
- [ ] Storage credentials configured.
- [ ] Bootstrap passwords removed after bootstrap or rotated.

## Domain And TLS

- [ ] Production domain configured.
- [ ] TLS configured.
- [ ] HTTP redirects to HTTPS.
- [ ] HSTS decision approved.
- [ ] CORS origins explicitly configured before public launch.

## Verification

- [ ] `ruff check backend frontend`
- [ ] `ruff format --check backend frontend`
- [ ] `python -m pytest backend/tests`
- [ ] `npm run lint`
- [ ] `npm run test`
- [ ] `npm run build`
- [ ] `npm run generate:api-types`
- [ ] `docker compose up -d --build`
- [ ] `docker compose exec api alembic upgrade head`

## Pilot Decision

Pilot launch requires:

- Backup and restore evidence.
- Monitoring evidence.
- Health check evidence.
- Secrets validation evidence.
- Incident owner assignment.
