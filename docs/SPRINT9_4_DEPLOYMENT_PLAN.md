# Sprint 9.4 Deployment Plan

## Target Deployment Direction

Pilot production should use managed infrastructure:

- Cloud Run or equivalent container runtime
- Cloud SQL PostgreSQL or equivalent managed PostgreSQL
- Managed Redis or equivalent cache
- Private object storage bucket
- TLS-managed domain
- Centralized logging and metrics

## Current Repository State

- Docker Compose exists for local and production-like deployment.
- No Terraform files are present.
- No Cloud Run service definition is present.
- No production health check split exists before Sprint 9.4.

## Cloud Run Requirements

- Container image built from backend service.
- `APP_ENV=production`.
- Strong JWT and secret configuration.
- Dedicated integration encryption key.
- Database URL via secret.
- Redis URL via secret.
- Object storage credentials via secret.
- Readiness endpoint: `/health/ready`.
- Liveness endpoint: `/health/live`.
- Minimum instance and concurrency policy defined.
- Request timeout selected based on API behavior.

## Cloud SQL Requirements

- Automated backups.
- PITR for production.
- Private connectivity preferred.
- Migration runbook.
- Connection pool sizing.

## Storage Requirements

- Private bucket.
- Signed URL access for protected media.
- Lifecycle rules.
- Versioning or replication.
- Access logging.

## Redis Requirements

- Production rate limiting depends on Redis.
- Redis must be monitored.
- Redis failure should produce operational alerts.

## Domain And TLS

- Managed TLS.
- Forced HTTPS.
- HSTS after verification.
- CORS policy before public launch.

## Deployment Gates

- `ruff check backend frontend`
- `ruff format --check backend frontend`
- `python -m pytest backend/tests`
- `npm run lint`
- `npm run test`
- `npm run build`
- `npm run generate:api-types`
- `docker compose up -d --build`
- `docker compose exec api alembic upgrade head`

## Remaining Gap

Terraform or infrastructure-as-code should be added in a later sprint once the
pilot platform is selected.
