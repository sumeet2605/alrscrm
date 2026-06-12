# Deployment Signoff

## Scope

Deployment readiness sprint for DigitalOcean UAT. No product features were
added.

## Changes Made

- Added `frontend/Dockerfile` for production Vite build and static nginx serve.
- Added `frontend/nginx.conf` for SPA fallback and frontend liveness.
- Added `nginx/nginx.conf` as the public reverse proxy.
- Updated `docker-compose.yml` to include `frontend` and `nginx`.
- Added health checks for `api`, `frontend`, `db`, `redis`, and `nginx`.
- Updated startup ordering so API waits for healthy database and Redis, frontend
  waits for healthy API, and nginx waits for healthy API and frontend.
- Removed development-only backend bind mount and `uvicorn --reload` from the
  compose startup command.

## Verification Results

Verified on 2026-06-11 local environment.

| Check | Result |
| --- | --- |
| `docker compose config` | Passed |
| `npm run build` from `frontend/` | Passed |
| `python -m pytest backend/tests/test_health.py` | Passed: 8 tests |
| `docker compose build api frontend` | Passed |
| `docker compose up -d` | Passed |
| `docker compose ps` | All five services healthy |
| Nginx `/health/live` through host port 80 | Passed |
| Nginx `/health/ready` through host port 80 | Passed |
| Frontend HTML through host port 80 | Passed |
| Internal nginx to API readiness | Passed |

Readiness payload confirmed:

```json
{
  "status": "ready",
  "checks": {
    "database": {"ok": true},
    "storage": {"ok": true},
    "migrations": {
      "ok": true,
      "current": "202606100019",
      "head": "202606100019"
    }
  }
}
```

## Container Readiness

| Container | Status |
| --- | --- |
| `frontend` | Verified build and Docker health check |
| `api` | Verified build, liveness, readiness, migrations |
| `db` | Verified PostgreSQL health check |
| `redis` | Verified Redis health check |
| `nginx` | Verified reverse proxy health check and host routing |

## Deployment Controls

- Migrations execute with `alembic upgrade head` before API traffic starts.
- Readiness fails if database connectivity fails.
- Readiness fails if Alembic current revision does not match head.
- Readiness fails if Spaces bucket access fails when Spaces storage is enabled.
- Public traffic should enter through nginx or a DigitalOcean Load Balancer.

## Known Warnings

- Frontend build reports a large JavaScript chunk warning. This is not a UAT
  deployment blocker.
- Docker frontend build reports npm audit findings from existing dependencies.
  No dependency upgrades were made in this sprint because the request was
  deployment readiness only.
- Compose binds `8000`, `5432`, and `6379` to `127.0.0.1` for local/UAT
  operations. DigitalOcean firewall rules should still block public access to
  those ports.
- This workstation already had a host PostgreSQL process on `127.0.0.1:5432`;
  final local stack verification used `POSTGRES_PORT=55432`. Container-to-
  container database traffic still used `db:5432`.

## UAT Signoff

Status: ready for DigitalOcean UAT deployment after real UAT secrets, Spaces
bucket credentials, DNS, SSL, and backup evidence are provisioned.

Production status: not signed off until managed backup/restore evidence, SSL,
firewall, and dependency security review are completed.
