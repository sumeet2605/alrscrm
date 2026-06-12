# UAT Go-Live Review

Review date: 2026-06-12

## Verdict

GO WITH FIXES

ALRSCRM is code-ready for a private DigitalOcean UAT go-live after operational
deployment fixes are completed: UAT secrets, private Spaces configuration, SSL,
backup/restore evidence, and Redis availability controls. No critical code
blocker was found during this review.

This is not a public SaaS production signoff.

## Review Scope

- Repository deployment configuration.
- Alembic migration state.
- Backend API route registration and permission coverage.
- Frontend routes and navigation guards.
- Health endpoints.
- Demo workflow coverage:
  Opportunity -> Booking -> Gallery -> Editing -> Delivery -> Invoice -> Payment.
- Production environment variable requirements.
- Sprint 8.1 and Sprint 9.2 security regression check.

## Verification Evidence

| Check | Result |
| --- | --- |
| Backend test suite | Passed: 71 tests |
| Frontend test suite | Passed: 37 tests |
| Frontend type/lint check | Passed |
| Frontend production build | Passed |
| Compose services | `api`, `db`, `redis`, `frontend`, and `nginx` healthy |
| Alembic current | `202606100019 (head)` |
| Alembic heads | `202606100019 (head)` |
| Registered FastAPI routes | 152 total, 145 under `/api/v1` |
| Nginx liveness | Passed |
| Nginx readiness | Passed |

Commands run:

```bash
python -m pytest backend/tests
npm test
npm run lint
npm run build
docker compose ps
docker compose exec api alembic current
docker compose exec api alembic heads
curl -fsS http://127.0.0.1:80/health/live
curl -fsS http://127.0.0.1:80/health/ready
```

## Migrations

Status: PASS

The running API container reports:

```text
202606100019 (head)
```

Readiness also reports:

```json
{
  "migrations": {
    "ok": true,
    "current": "202606100019",
    "head": "202606100019"
  }
}
```

## Routes

Status: PASS

All route modules are included in `backend/app/api/router.py`:

- Auth
- Organizations
- Branches
- Users
- RBAC
- Families
- Opportunities, follow-ups, lost reasons
- Bookings, packages, addons, schedules, assignments
- Galleries
- Editing
- Delivery
- Finance, invoices, payments
- Integrations
- Platform health metrics

FastAPI route inspection found 152 registered routes, including 145 API routes
under `/api/v1`.

## Frontend Navigation

Status: PASS WITH NON-BLOCKING CLEANUP

Frontend routes exist for the UAT workflow and operational areas:

- `/sales`, `/sales/opportunities`, `/sales/opportunities/new`
- `/bookings`, `/bookings/new`
- `/galleries`, `/galleries/:galleryId`, `/galleries/:galleryId/upload`
- `/production`, `/production/editing`, `/production/editing/:jobId`
- `/delivery`, `/delivery/dashboard`, `/delivery/:deliveryId`
- `/finance`, `/finance/invoices`, `/finance/payments`
- `/settings/integrations`

Navigation tests passed. A non-blocking cleanup remains in
`frontend/src/routes/routePermissions.ts`: the public gallery guard allows
`/client/galleries...`, while the actual public route is `/client/gallery/:token`.
The actual public route is outside `ProtectedRoute`, so this did not block
reachability or tests.

## Permissions

Status: PASS

Backend domain routes generally use `require_permissions(...)`. Permission seed
coverage includes the current UAT domains:

- Sales: `sales:*`
- Bookings: `bookings:*`
- Galleries: `galleries:*`
- Editing: `editing:*`
- Delivery: `delivery:*`
- Finance: `finance:*`
- Integrations: `integrations:*`
- Platform health: `platform:health:metrics`

Role coverage is aligned with expected UAT users:

- Super Admin: platform and tenant permissions.
- Organization Admin and Owner: full tenant access except platform organization
  administration.
- Branch Manager: branch operational access, including finance and integrations.
- Sales Executive, Photographer, Editor, and Customer Success: scoped workflow
  access.

Frontend route permission tests passed, and backend authorization tests cover
tenant/branch denial paths across sales, finance, editing, delivery, galleries,
and integrations.

## Health Endpoints

Status: PASS

Verified through nginx:

```text
GET /health/live -> {"status":"live"}
GET /health/ready -> status ready
```

Readiness checks:

- Database connectivity.
- Storage provider access.
- Alembic current revision equals head.

## Demo Workflow

Status: PASS BY DOMAIN COVERAGE

The full UAT demo path is covered by passing backend tests across connected
domains:

1. Opportunity
   - Opportunity creation, pipeline, follow-ups, stage history, metrics, and
     booked read-only behavior passed.
2. Booking
   - Booking creation from booked opportunity, package/addon pricing, schedules,
     assignments, photographer visibility, and metrics passed.
3. Gallery
   - Gallery creation, photo upload, access-token rotation, client favorites,
     public token access, and metrics passed.
4. Editing
   - Submitted gallery creates editing job; assign, start, submit review,
     approve, mark ready for delivery, and metrics passed.
5. Delivery
   - Ready-for-delivery creates delivery job; generate ZIP, send, public
     authenticate, download audit, password protection, expiry, token revocation,
     reopen, and rate-limit behavior passed.
6. Invoice
   - Finance settings, invoice creation, issue, PDF generation, and metrics
     passed.
7. Payment
   - Payment creation, receipt PDF, invoice balance update, overpayment
     rejection, and tenant/branch access controls passed.

Residual note: these are domain-spanning tests, not one single browser-driven
E2E scenario from Opportunity through Payment. For UAT go-live this is
acceptable; before public launch, add a single Playwright or API E2E smoke
test that executes the entire flow as one scripted demo.

## Production Environment Variables

Status: PASS WITH DEPLOYMENT ACTIONS

Application settings are documented in
`docs/PRODUCTION_ENVIRONMENT_VARIABLES.md`. Non-local startup requires strong:

- `SECRET_KEY`
- `JWT_SECRET` or `JWT_SECRET_KEY`
- `INTEGRATION_ENCRYPTION_KEY`

Spaces mode requires:

- `STORAGE_PROVIDER=spaces`
- `DO_SPACES_REGION`
- `DO_SPACES_BUCKET`
- `DO_SPACES_ACCESS_KEY`
- `DO_SPACES_SECRET_KEY`
- Recommended: `DO_SPACES_ENDPOINT_URL`
- Recommended: keep `DO_SPACES_CDN_URL` unset for protected media unless CDN
  private-access controls are explicitly validated.

Compose-level UAT variables also need to be set:

- `BACKEND_ENV_FILE`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `BOOTSTRAP_ADMIN_PASSWORD` for first deploy
- `VITE_API_BASE_URL`
- `HTTP_PORT`

## Sprint 8.1 Security Regression Review

Status: PASS

No Sprint 8.1 regression was detected in this review:

- Tenant-aware login model remains in place.
- Bootstrap production secret validation exists.
- Public Gallery token routes exist and tests confirm UUID public route access is
  rejected.
- Public Gallery expiry/password behavior is covered by tests.
- Audit records include request IDs in health/security tests.
- Backend tenant/branch scope tests passed.

## Sprint 9.2 Security Regression Review

Status: PASS

No Sprint 9.2 regression was detected in this review:

- `INTEGRATION_ENCRYPTION_KEY` is required in non-local environments.
- Integration credentials remain encrypted/masked in API behavior.
- Integration APIs use `integrations:view` and `integrations:manage`.
- Integration tenant/branch tests passed.
- Invoice PDF and payment receipt PDF tests passed.
- Finance route permissions and tenant/branch scoping tests passed.

## Required UAT Fixes Before Go-Live

These are operational fixes, not feature work:

1. Provision real UAT secrets and point compose at `BACKEND_ENV_FILE`.
2. Configure private DigitalOcean Spaces and verify `/health/ready` with
   `storage.ok=true` against the real bucket.
3. Deploy SSL using a DigitalOcean Load Balancer or documented Certbot/nginx
   process.
4. Confirm firewall blocks public `8000`, `5432`, and `6379`; nginx or the load
   balancer must be the public entry point.
5. Complete and record one database backup.
6. Complete and record one restore drill or approved restore rehearsal.
7. Ensure Redis is available and monitored for auth rate limiting.
8. Accept known private-pilot risks from `docs/SPRINT9_3_SECURITY_REVIEW.md`,
   especially provider-level integration verification, public-flow monitoring,
   and finance PDF statutory validation.

## Non-Blocking Warnings

- Frontend build still reports a large bundle warning.
- Frontend tests emit an existing Ant Design `act(...)` warning.
- Backend tests emit existing datetime deprecation warnings in Gallery selection
  tests.
- Frontend build reports a dynamic/static import warning for Gallery API usage.
- Local verification used `POSTGRES_PORT=55432` because this workstation already
  had PostgreSQL listening on `127.0.0.1:5432`.

## Final Decision

GO WITH FIXES

Proceed to DigitalOcean UAT only after the required operational fixes above are
completed and recorded. Do not treat this as a public production launch approval.

