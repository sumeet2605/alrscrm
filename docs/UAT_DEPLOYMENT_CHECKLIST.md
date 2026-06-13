# UAT Deployment Checklist

## Pre-Deployment

- [ ] Droplet created with supported Ubuntu LTS image.
- [ ] Docker Engine and Docker Compose plugin installed.
- [ ] DNS record created for UAT hostname.
- [ ] Cloud firewall allows public `80` and `443`.
- [ ] Cloud firewall blocks public `5432`, `6379`, and `8000`.
- [ ] `backend/.env.uat` created outside version control.
- [ ] `BACKEND_ENV_FILE=backend/.env.uat` exported for compose commands.
- [ ] Strong `POSTGRES_PASSWORD` set.
- [ ] Strong `SECRET_KEY` set.
- [ ] Strong `JWT_SECRET` or `JWT_SECRET_KEY` set.
- [ ] Strong `INTEGRATION_ENCRYPTION_KEY` set.
- [ ] Temporary `BOOTSTRAP_ADMIN_PASSWORD` set and stored securely.
- [ ] `ENVIRONMENT=uat` or `ENVIRONMENT=production` set.
- [ ] `APP_DEBUG=false` set.

## Storage

- [ ] DigitalOcean Space created.
- [ ] Space is private.
- [ ] Access key has only required bucket access.
- [ ] `STORAGE_PROVIDER=spaces` set.
- [ ] `DO_SPACES_REGION` set.
- [ ] `DO_SPACES_BUCKET` set.
- [ ] `DO_SPACES_ACCESS_KEY` set.
- [ ] `DO_SPACES_SECRET_KEY` set.
- [ ] `DO_SPACES_ENDPOINT_URL` set.
- [ ] `DO_SPACES_PATH_PREFIX` set to a UAT-specific prefix.
- [ ] `/health/ready` confirms `storage.ok=true`.

## Build And Startup

- [ ] `docker compose config` succeeds.
- [ ] `docker compose build api frontend` succeeds.
- [ ] `docker compose up -d` succeeds.
- [ ] `db` is healthy.
- [ ] `redis` is healthy.
- [ ] `api` is healthy.
- [ ] `frontend` is healthy.
- [ ] `nginx` is healthy.
- [ ] `docker compose ps` shows all five services running.

## Health Checks

- [ ] `curl -fsS http://127.0.0.1/health/live` returns `{"status":"live"}`.
- [ ] `curl -fsS http://127.0.0.1/health/ready` returns `status=ready`.
- [ ] Readiness shows `database.ok=true`.
- [ ] Readiness shows `storage.ok=true`.
- [ ] Readiness shows `migrations.ok=true`.
- [ ] Frontend HTML is served through nginx.
- [ ] `/api/v1` traffic is routed through nginx to the backend.

## SSL

- [ ] DigitalOcean Load Balancer created or single-droplet Certbot process approved.
- [ ] Certificate issued for the UAT hostname.
- [ ] HTTP to HTTPS redirect enabled.
- [ ] Browser shows a valid certificate chain.
- [ ] API requests work through HTTPS origin.

## Migrations

- [ ] Current database Alembic version recorded before deploy.
- [ ] Target Alembic head recorded.
- [ ] `alembic upgrade head` completed.
- [ ] `/health/ready` confirms current revision equals head.
- [ ] No manual schema changes applied outside Alembic.

## Backup And Restore

- [ ] Database backup completed before deployment.
- [ ] Backup identifier, timestamp, and Alembic version recorded.
- [ ] Spaces backup/versioning/replication verified.
- [ ] Restore drill completed in UAT or staging.
- [ ] Restore duration recorded.
- [ ] RPO and RTO accepted by owner.

## Smoke Tests

- [ ] Super admin login works.
- [ ] Tenant login works.
- [ ] Families list loads.
- [ ] Booking workflow loads.
- [ ] Gallery upload or sample gallery access works.
- [ ] Delivery artifact access works.
- [ ] Finance page loads.
- [ ] Integration health page loads.
- [ ] Audit/request IDs continue appearing in logs.

## Go/No-Go

- [ ] No critical deployment blockers remain.
- [ ] Known warnings are documented in `docs/DEPLOYMENT_SIGNOFF.md`.
- [ ] UAT owner approves release.

