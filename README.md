
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
- JWT access/refresh tokens
- Password hashing
- Role based authorization
- Alembic migration and RBAC seed script

## Backend Quick Start

```bash
docker compose up --build
```

The API runs at `http://localhost:8000`.

Useful commands:

```bash
cd backend
alembic upgrade head
python scripts/seed_identity.py
uvicorn app.main:app --reload
```

## API

All Sprint 1 endpoints are under `/api/v1`.

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
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

## Tests and Lint

```bash
pip install -r backend/requirements.txt
pytest
ruff check backend
```
