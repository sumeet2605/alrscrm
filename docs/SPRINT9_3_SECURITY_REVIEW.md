# Sprint 9.3 Security Review

Review scope:

- Authentication
- JWT and refresh token security
- RBAC and API authorization
- Public Gallery and Delivery security
- Finance and tenant integrations security
- Audit logging
- Secrets and deployment exposure

No backend, frontend, or migration code was modified for this review.

## Security Verdict

```text
GO WITH FIXES for private pilot.
NO GO for public SaaS launch until BLOCKER and HIGH items are resolved.
```

## Security Findings

| Severity | Finding | Evidence | Recommendation |
| --- | --- | --- | --- |
| HIGH | Login rate limiting falls back to per-process memory if Redis is unavailable. | `backend/app/auth/rate_limit.py` | In production, use highly available Redis and fail closed or degrade with an explicit operational alert. |
| HIGH | Platform administration still uses a tenant-shaped pseudo organization. | `docs/PLATFORM_VS_TENANT_ARCHITECTURE_REVIEW.md` | Migrate Super Admin to platform-scoped identity in a dedicated architecture sprint. |
| HIGH | Integration encryption can derive from `JWT_SECRET_KEY` when a dedicated integration key is not configured. | `backend/app/core/config.py`, `backend/app/core/crypto.py` | Require `INTEGRATION_ENCRYPTION_KEY` in non-local environments and document rotation. |
| HIGH | Integration verification marks credentials as connected after shape validation only. | `backend/app/integrations/services/integration_service.py` | Verify credentials against WhatsApp, Meta, SMTP, GCS, and S3 provider APIs before showing connected. |
| HIGH | DigitalOcean CDN URL configuration can return public CDN URLs instead of signed URLs. | `backend/app/galleries/storage/provider.py` | Require private CDN controls or disable CDN URL for protected media. |
| HIGH | Production deployment lacks complete secret management and edge security configuration. | `docker-compose.prod.yml`, `backend/.env.example` | Use a secret manager or protected environment injection; add TLS/reverse proxy/WAF decisions. |
| MEDIUM | Public Gallery and Delivery flows need explicit abuse-rate limits and anomaly alerts. | `backend/app/galleries/routes.py`, `backend/app/delivery/routes.py` | Add token/IP throttling, failed password counters, and alerting. |
| MEDIUM | Audit event coverage is not yet governed by a complete event matrix. | `backend/app/shared/services/audit_service.py`, domain services | Define mandatory audit events by domain and verify with tests. |
| MEDIUM | Unexpected backend exceptions are not clearly wrapped with request IDs and sanitized structured logs. | `backend/app/main.py` | Add correlation IDs and global unexpected exception logging that avoids secret leakage. |
| MEDIUM | Frontend route permissions are only UI guards. | `frontend/src/routes/routePermissions.ts` | Continue treating backend permissions as authoritative; add tests to detect route/API drift. |
| MEDIUM | Finance PDFs need legal/compliance validation before external use. | `backend/app/finance/pdf.py` | Validate GST invoice and receipt output with accounting requirements. |
| LOW | Existing non-blocking frontend warnings remain in test/build output. | Sprint completion reports | Clean up warnings before launch hardening freeze. |

## Authentication Review

Current strengths:

- Login requires `organization_code`, `email`, and `password`.
- Organization lookup happens before user lookup.
- User lookup is scoped by `organization_id + email`.
- Password validation remains unchanged.
- Login audit events record tenant context where available.
- Duplicate email support across organizations is structurally supported.

Residual risk:

- Rate limiting depends on Redis availability but silently uses local memory on
  Redis failure.
- The current Super Admin login still depends on the pseudo-platform
  organization model.

Recommendation:

```text
Require Redis availability for production authentication or fail closed with a
clear operational alert.
```

## JWT And Refresh Token Review

Current strengths:

- Access and refresh tokens include `organization_id` and `branch_id` claims.
- Refresh tokens include a token identifier.
- Refresh token identifiers are hashed before persistence.
- Refresh token rotation is implemented.
- Reuse or invalid state revokes user sessions.

Residual risk:

- Platform-scoped future JWTs will need a different `scope` model because the
  current token shape assumes tenant context.

Recommendation:

```text
Do not remove ALRSCRM or change platform login until platform-scoped JWT and
authorization contexts are implemented.
```

## Public Gallery Security

Current strengths:

- Public Gallery access was moved away from UUID-as-secret.
- Tokenized public access supports expiry, revocation, and rotation.
- Expired Gallery authentication and selection paths were hardened in Sprint
  8.1.

Residual risk:

- Public route abuse controls should be made explicit.
- Operators need a documented link rotation and incident response playbook.

Recommendation:

```text
Add IP/token rate limits, failed-auth counters, and public access audit review
before open client traffic.
```

## Delivery Security

Current strengths:

- Public delivery access uses opaque tokens.
- Token hashes are stored instead of raw tokens.
- Delivery passwords are hashed.
- Temporary public delivery sessions are used.
- Signed artifact URLs are generated.
- Reopen request cooldown/rate limits exist.

Residual risk:

- Delivery artifact generation needs a worker model and monitoring.
- Download abuse should be observable in dashboards or logs.

Recommendation:

```text
Keep Delivery public access enabled only with monitoring and background worker
readiness.
```

## Finance Security

Current strengths:

- Finance is a separate bounded context.
- Finance APIs are tenant and branch scoped.
- Invoice and Payment are the financial source of truth.
- Booking monetary fields remain compatibility snapshots.

Risks:

- Invoice and receipt PDF formats require statutory validation before real GST
  use.
- Invoice/payment numbering should be reviewed for tenant sequence leakage and
  independent branch sequence requirements.

Recommendation:

```text
Treat Sprint 9.1 Finance as operational MVP, not final compliance-grade finance.
```

## Tenant Integrations Security

Current strengths:

- Credentials are encrypted at rest.
- API responses expose credential keys, not secret values.
- Integrations are tenant scoped and optionally branch scoped.
- Create, update, and verify actions are audited.

Risks:

- Credential verification does not call provider APIs.
- Dedicated encryption key should be mandatory in production.
- Secret rotation and provider expiry handling are not yet complete.

Recommendation:

```text
Do not call an integration CONNECTED in production until provider-level
verification succeeds.
```

## API Authorization Review

Current strengths:

- Domain routes generally use `require_permissions`.
- Services enforce tenant and branch scope.
- Public routes are separated from authenticated staff routes.

Risks:

- Platform routes and tenant routes still share a single user identity model.
- Public endpoints need more abuse-oriented regression tests.

Recommendation:

```text
Add a security regression suite that asserts every authenticated route has a
permission dependency and every repository query has tenant scope.
```

## Audit Security Review

Current strengths:

- Audit logs include tenant and branch scope after Sprint 8.1 hardening.
- Authentication, integration, delivery, gallery, finance, and editing actions
  emit audit events in key workflows.

Risks:

- No complete audit event matrix exists.
- No production audit search/export workflow is present.
- Platform audit semantics are still coupled to the pseudo-platform tenant.

Recommendation:

```text
Define an audit coverage matrix and add tenant-safe audit query APIs before
regulated production use.
```

## Security Launch Decision

```text
NO GO for public SaaS launch.
GO WITH FIXES for private pilot after Redis, secret, storage, and monitoring
controls are enforced.
```
