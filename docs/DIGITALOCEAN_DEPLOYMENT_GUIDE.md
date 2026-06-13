# DigitalOcean Deployment Guide

## Scope

This guide deploys ALRSCRM to a DigitalOcean UAT droplet with Docker Compose.
It does not add product features. The deployment stack is:

- `nginx`: public reverse proxy on port 80.
- `frontend`: Vite build served by nginx.
- `api`: FastAPI backend.
- `db`: PostgreSQL 16.
- `redis`: Redis 7 with append-only persistence.

For production, prefer DigitalOcean Managed PostgreSQL, Managed Redis, and a
DigitalOcean Load Balancer. For UAT, the compose-managed database and Redis are
acceptable only if backups and firewall rules are enabled.

## Droplet Prerequisites

1. Create an Ubuntu LTS droplet.
2. Point the UAT DNS record to the droplet or to a DigitalOcean Load Balancer.
3. Install Docker Engine and the Docker Compose plugin.
4. Allow inbound `80` and `443` only from the public internet.
5. Restrict `22` to trusted IPs.
6. Do not expose `5432`, `6379`, or `8000` publicly in the cloud firewall.

## Deployment Files

- Compose file: `docker-compose.yml`
- Backend image: `backend/Dockerfile`
- Frontend image: `frontend/Dockerfile`
- Frontend static nginx config: `frontend/nginx.conf`
- Edge reverse proxy config: `nginx/nginx.conf`
- Backend env template: `backend/.env.example`

## Environment Setup

Create a UAT env file outside version control, for example:

```bash
cp backend/.env.example backend/.env.uat
chmod 600 backend/.env.uat
```

Set the compose env file selector before deployment:

```bash
export BACKEND_ENV_FILE=backend/.env.uat
export POSTGRES_DB=alrscrm
export POSTGRES_USER=alrscrm
export POSTGRES_PASSWORD='<strong-postgres-password>'
export BOOTSTRAP_ADMIN_PASSWORD='<temporary-bootstrap-password>'
export VITE_API_BASE_URL=/api/v1
```

GitHub Actions UAT deployment auto-selects `backend/.env.uat` when present,
otherwise `backend/.env`, otherwise root `.env`. The selected backend env file must set
`STORAGE_PROVIDER=spaces`, `digitalocean`, or `do_spaces`; otherwise deployment
stops before `docker compose up` so uploads cannot silently fall back to local
storage.

If the host already runs PostgreSQL, use an alternate loopback host port for
local diagnostics:

```bash
export POSTGRES_PORT=55432
```

Populate `backend/.env.uat` using
`docs/PRODUCTION_ENVIRONMENT_VARIABLES.md`.

## Build And Start

```bash
docker compose config
docker compose build api frontend
docker compose up -d
docker compose ps
```

Expected startup order:

1. `db` starts and passes `pg_isready`.
2. `redis` starts and passes `redis-cli ping`.
3. `api` starts after database and Redis are healthy.
4. `api` runs `alembic upgrade head`, identity seed, sales seed, and super
   admin seed before serving traffic.
5. `frontend` starts after the API liveness check is healthy.
6. `nginx` starts after API and frontend are healthy.

## Health Verification

Run through the public nginx entry point:

```bash
curl -fsS http://127.0.0.1/health/live
curl -fsS http://127.0.0.1/health/ready
curl -fsSI http://127.0.0.1/
```

Expected liveness:

```json
{"status":"live"}
```

Expected readiness:

```json
{
  "status": "ready",
  "checks": {
    "database": {"ok": true},
    "storage": {"ok": true},
    "migrations": {"ok": true}
  }
}
```

## DigitalOcean Spaces

For UAT object storage, create a private Space and an access key with the
minimum bucket permissions required for object read/write/delete.

Required backend settings:

```bash
STORAGE_PROVIDER=spaces
DO_SPACES_REGION=blr1
DO_SPACES_BUCKET=<uat-space-name>
DO_SPACES_ACCESS_KEY=<spaces-access-key>
DO_SPACES_SECRET_KEY=<spaces-secret-key>
DO_SPACES_ENDPOINT_URL=https://blr1.digitaloceanspaces.com
DO_SPACES_CDN_URL=
DO_SPACES_PATH_PREFIX=alrscrm/uat
```

Readiness calls `head_bucket` for Spaces-backed storage, so
`/health/ready` fails if credentials, region, bucket name, endpoint, or network
access are wrong.

## SSL Deployment

Recommended UAT setup:

1. Create a DigitalOcean Load Balancer.
2. Attach the droplet as the backend target on port `80`.
3. Add a DigitalOcean managed certificate for the UAT hostname.
4. Redirect HTTP to HTTPS at the load balancer.
5. Keep container traffic private HTTP from load balancer to nginx.

Alternative single-droplet setup:

1. Install Certbot on the host.
2. Issue a certificate for the UAT hostname.
3. Add an SSL server block to `nginx/nginx.conf`.
4. Mount the certificate directory read-only into the nginx container.
5. Reload nginx after certificate renewal.

Do not deploy UAT with browser traffic over plain HTTP except for temporary
smoke testing before DNS and certificate activation.

## Backup

For UAT on compose-managed PostgreSQL:

```bash
mkdir -p backups
docker compose exec db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > backups/alrscrm-uat-$(date +%Y%m%d%H%M).dump
docker compose exec api alembic current
```

For Spaces, enable bucket versioning or replicate the bucket. Record the bucket,
prefix, timestamp, and sample object restore verification. See
`docs/BACKUP_RUNBOOK.md` for the operational checklist.

## Restore

Database restore to a fresh database:

```bash
docker compose down
docker volume create alrscrm_postgres_data_restore
docker compose up -d db redis
cat backups/<backup-file>.dump | docker compose exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists
docker compose up -d api frontend nginx
curl -fsS http://127.0.0.1/health/ready
```

Storage restore depends on the Spaces backup mechanism. Restore the affected
object versions or replicated prefix, then verify signed URL generation through
the application. See `docs/RESTORE_RUNBOOK.md`.

## Migration Process

The API container executes `alembic upgrade head` during startup before serving
requests. For controlled UAT rollout:

```bash
docker compose run --rm api alembic current
docker compose run --rm api alembic heads
docker compose run --rm api alembic upgrade head
docker compose up -d api frontend nginx
curl -fsS http://127.0.0.1/health/ready
```

Do not downgrade production or UAT databases without a tested restore plan.
