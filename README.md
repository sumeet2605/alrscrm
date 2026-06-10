
# ALRSCRM

Premium Family Photography Studio Operating System for maternity, newborn, and family
photography studios.

## Sprint 1 Scope

Sprint 1 implements Identity & Access:

- Organizations CRUD
- Branches CRUD
- Users CRUD
- Roles read API
- Permissions read API
- Login, refresh token, and authenticated user lookup
- Logout with refresh-token revocation
- JWT access/refresh tokens
- Password hashing
- Role based authorization
- Alembic migration and RBAC seed script
- Tenant and branch-aware authorization
- Soft deactivation for identity records
- Pagination metadata on list endpoints

## Backend Quick Start

```bash
docker compose up --build
```

The API runs at `http://localhost:8000`.

If a previous first run failed while Postgres was initializing, reset the local
containers and volume before retrying:

```bash
docker compose down -v
docker compose up --build
```

Local Docker startup seeds this super admin account:

```text
username: admin
email: admin@admin.com
password: Admin@123
```

Useful commands:

```bash
cd backend
alembic upgrade head
python -m scripts.seed_identity
python -m scripts.seed_super_admin
uvicorn app.main:app --reload
```

## API

All Sprint 1 endpoints are under `/api/v1`.

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET|POST /api/v1/organizations`
- `GET|PATCH|DELETE /api/v1/organizations/{organization_id}`
- `GET|POST /api/v1/branches`
- `GET|PATCH|DELETE /api/v1/branches/{branch_id}`
- `GET|POST /api/v1/users`
- `GET|PATCH|DELETE /api/v1/users/{user_id}`
- `GET /api/v1/roles`
- `GET /api/v1/permissions`

Responses use this envelope:

```json
{
  "success": true,
  "message": "string",
  "data": {}
}
```

List endpoints keep `data` as an array for backwards compatibility and include
pagination details in `meta`:

```json
{
  "success": true,
  "message": "Organizations retrieved",
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 0,
    "pages": 0
  }
}
```

## Production Notes

- Set `ENVIRONMENT` to a non-local value and provide a strong `JWT_SECRET_KEY`.
- Run `alembic upgrade head` and `python -m scripts.seed_identity` as release
  steps before starting API workers.
- Use `docker-compose.prod.yml` as the production-oriented Compose baseline.
- Refresh tokens are persisted and rotated; use `/api/v1/auth/logout` to revoke
  a refresh token.

## Tests and Lint

```bash
pip install -r backend/requirements.txt
pytest
ruff check backend
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api` requests to the
backend on `http://localhost:8000`.

Frontend verification:

```bash
cd frontend
npm run lint
npm run test
npm run build
```
