# Sprint 1 Completion Report

## Files Created

- Backend application structure under `backend/app/`
- Core configuration, database, and security modules
- Authentication routes, schemas, and services
- Identity models, schemas, services, routes, and seed definitions
- Shared response and exception helpers
- Alembic configuration and initial identity/access migration
- RBAC seed script at `backend/scripts/seed_identity.py`
- Backend tests under `backend/tests/`
- Dockerfile and Docker Compose setup
- GitHub Actions workflow for lint, test, and build
- Project lint/test configuration in `pyproject.toml`
- Environment example in `backend/.env.example`

## Architecture Decisions

- Implemented Sprint 1 as an Identity & Access bounded context with separate
  models, schemas, services, and routes.
- Kept route handlers thin and moved persistence behavior into service modules.
- Used SQLAlchemy 2.0 declarative mappings with UUID primary keys.
- Used Pydantic v2 schemas for request validation and response serialization.
- Used JWT access and refresh tokens with explicit token type claims.
- Seeded roles and permissions through an idempotent seed function, invoked by
  both startup and the dedicated seed script.
- Enforced RBAC through FastAPI dependencies that validate assigned role
  permissions before protected identity endpoints execute.
- Standardized API responses with the required `success`, `message`, and `data`
  envelope.

## Endpoints

All endpoints are prefixed by `/api/v1`.

- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /organizations`
- `POST /organizations`
- `GET /organizations/{organization_id}`
- `PATCH /organizations/{organization_id}`
- `DELETE /organizations/{organization_id}`
- `GET /branches`
- `POST /branches`
- `GET /branches/{branch_id}`
- `PATCH /branches/{branch_id}`
- `DELETE /branches/{branch_id}`
- `GET /users`
- `POST /users`
- `GET /users/{user_id}`
- `PATCH /users/{user_id}`
- `DELETE /users/{user_id}`
- `GET /roles`
- `GET /permissions`

## Database Schema

- `organizations`: id, name, code, is_active, created_at, updated_at
- `branches`: id, organization_id, name, code, city, address, phone, email,
  is_active, created_at, updated_at
- `users`: id, organization_id, branch_id, email, password_hash, first_name,
  last_name, phone, is_active, created_at, updated_at
- `roles`: id, name, description
- `permissions`: id, code, name, description
- `user_roles`: user_id, role_id
- `role_permissions`: role_id, permission_id
- `refresh_token_sessions`: id, user_id, token_hash, replaced_by_token_id,
  expires_at, revoked_at, ip_address, user_agent, created_at
- `audit_logs`: id, actor_user_id, action, target_type, target_id,
  metadata_json, created_at

## How To Run Locally

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

Manual backend commands:

```bash
cd backend
alembic upgrade head
python scripts/seed_identity.py
uvicorn app.main:app --reload
```

Verification commands:

```bash
pip install -r backend/requirements.txt
ruff check backend
pytest
```
