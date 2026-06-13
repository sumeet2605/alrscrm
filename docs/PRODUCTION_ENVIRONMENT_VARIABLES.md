# Production Environment Variables

## Compose-Level Variables

These are read by `docker-compose.yml` before containers start.

| Variable | Required | Example | Notes |
| --- | --- | --- | --- |
| `BACKEND_ENV_FILE` | Yes | `backend/.env.uat` | Selects the backend env file. |
| `POSTGRES_DB` | Yes | `alrscrm` | Must match `DATABASE_URL`. |
| `POSTGRES_USER` | Yes | `alrscrm` | Must match `DATABASE_URL`. |
| `POSTGRES_PASSWORD` | Yes | strong secret | Do not use the local default. |
| `BOOTSTRAP_ADMIN_PASSWORD` | First deploy | strong temporary secret | Rotate after first login. |
| `VITE_API_BASE_URL` | Yes | `/api/v1` | Build-time frontend API base URL. |
| `HTTP_PORT` | No | `80` | Public nginx HTTP port. |
| `API_PORT` | No | `8000` | Host loopback port for backend diagnostics. |
| `POSTGRES_PORT` | No | `5432` | Host loopback port for database diagnostics. |
| `REDIS_PORT` | No | `6379` | Host loopback port for Redis diagnostics. |

## Backend Application Variables

Set these in the file referenced by `BACKEND_ENV_FILE`.

| Variable | Required | UAT/Production Value |
| --- | --- | --- |
| `APP_NAME` | Yes | `ALRSCRM API` |
| `ENVIRONMENT` | Yes | `uat` or `production` |
| `APP_DEBUG` | Yes | `false` |
| `API_V1_PREFIX` | Yes | `/api/v1` |
| `SECRET_KEY` | Yes | At least 32 high-entropy characters |
| `DATABASE_URL` | Yes | `postgresql+psycopg://<user>:<password>@db:5432/<db>` |
| `DATABASE_POOL_SIZE` | Yes | Start with `5` for UAT |
| `DATABASE_MAX_OVERFLOW` | Yes | Start with `10` for UAT |
| `REDIS_URL` | Yes | `redis://redis:6379/0` |
| `JWT_SECRET_KEY` or `JWT_SECRET` | Yes | At least 32 high-entropy characters |
| `JWT_ALGORITHM` | Yes | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | `30` |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Yes | `10080` |
| `INTEGRATION_ENCRYPTION_KEY` | Yes | At least 32 high-entropy characters |
| `STORAGE_PROVIDER` | Yes | `spaces` |
| `STORAGE_SIGNED_URL_EXPIRE_SECONDS` | Yes | `900` |
| `DO_SPACES_REGION` | Yes for Spaces | Example: `blr1` |
| `DO_SPACES_BUCKET` | Yes for Spaces | UAT or production bucket name |
| `DO_SPACES_ACCESS_KEY` | Yes for Spaces | Spaces access key |
| `DO_SPACES_SECRET_KEY` | Yes for Spaces | Spaces secret key |
| `DO_SPACES_ENDPOINT_URL` | Recommended | `https://blr1.digitaloceanspaces.com` |
| `DO_SPACES_CDN_URL` | Optional | CDN endpoint if used |
| `DO_SPACES_PATH_PREFIX` | Yes | `alrscrm/uat` or `alrscrm/prod` |
| `SEED_SAMPLE_TENANT` | Yes | `false` |
| `BOOTSTRAP_ADMIN_EMAIL` | First deploy | Admin email |
| `BOOTSTRAP_ADMIN_USERNAME` | First deploy | Admin username |
| `BOOTSTRAP_ADMIN_PASSWORD` | First deploy | Strong temporary password |
| `BOOTSTRAP_FORCE_PASSWORD_RESET` | Yes | `true` recommended |
| `SAMPLE_OWNER_PASSWORD` | No | Leave unset unless sample tenant is enabled |
| `SAMPLE_OWNER_FORCE_PASSWORD_RESET` | No | `false` unless sample tenant is enabled |

## Security Validation

When `ENVIRONMENT` is not `local`, `test`, or `development`, the backend rejects
startup unless these are strong and present:

- `SECRET_KEY`
- `JWT_SECRET` or `JWT_SECRET_KEY`
- `INTEGRATION_ENCRYPTION_KEY`

The backend also rejects non-positive token expiry and signed URL expiry values.

## Spaces Validation

When `STORAGE_PROVIDER` is `digitalocean`, `spaces`, or `do_spaces`, startup
requires:

- `DO_SPACES_REGION`
- `DO_SPACES_BUCKET`
- `DO_SPACES_ACCESS_KEY`
- `DO_SPACES_SECRET_KEY`

Readiness verifies bucket access with a Spaces `head_bucket` call.

## Variables Not For Git

Do not commit real values for:

- Database password
- Bootstrap admin password
- JWT secret
- Application secret key
- Integration encryption key
- Spaces access key
- Spaces secret key
