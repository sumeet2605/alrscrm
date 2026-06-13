# Tenant-Aware Login Design

Sprint 8 does not implement login changes. This document evaluates future login
options for ALRSCRM as a shared-database, shared-schema SaaS platform.

## Current Problem

Users are unique by:

```text
(organization_id, email)
```

But login currently accepts:

```text
email + password
```

and resolves the user by email only.

This means duplicate emails across customer tenants are valid at the database
level but ambiguous at login time.

## Option A: Global Unique Email

Require every email to be globally unique across the platform.

Pros:

- Simplest login UX.
- No tenant selector required.
- Lowest implementation complexity.

Cons:

- Conflicts with the current tenant-local user uniqueness model.
- One consultant, owner, or staff member cannot use the same email across
  multiple studios.
- Less flexible for SaaS.

Migration strategy:

- Detect duplicate emails across tenants.
- Resolve duplicates manually or require alternate login identifiers.
- Add a global unique email constraint only after cleanup.

## Option B: Organization Code And Email

Login with:

```text
organization_code + email + password
```

Pros:

- Matches current tenant-local email uniqueness.
- Explicit tenant boundary.
- Works without DNS or domain setup.
- Simple to test and operate.

Cons:

- Adds one more field to login.
- Users must know their organization code.
- Platform Super Admin needs a platform code such as `ALRSCRM`.

Migration strategy:

- Add optional organization code field to login UI.
- Keep email-only login temporarily for globally unique email matches.
- Prefer organization-code lookup when code is supplied.
- Later make organization code required.

## Option C: Subdomain Based Login

Login through:

```text
customer.alrscrm.com
```

Pros:

- Clean SaaS UX.
- Tenant context is resolved before login.
- Email remains tenant-local.

Cons:

- Requires DNS, routing, tenant slug management, and local dev support.
- More moving parts for early SaaS rollout.
- Platform admin login needs a platform subdomain or admin domain.

Migration strategy:

- Add `tenant_slug` to organization settings.
- Route subdomains to frontend.
- Resolve tenant from hostname before login.
- Keep organization-code fallback for admin and support.

## Option D: Custom Domain Login

Login through customer-owned domains.

Pros:

- Best white-label experience.
- Strong brand fit for larger studios.

Cons:

- Requires domain verification, TLS automation, DNS documentation, support
  tooling, and failure handling.
- Too much operational complexity for the first SaaS onboarding sprint.

Migration strategy:

- Implement after subdomain login.
- Add verified domain table.
- Add certificate automation.
- Keep platform fallback login.

## Recommendation

Recommended approach:

```text
Option B: Organization Code And Email
```

Reason:

- It fits the current database model.
- It preserves tenant-local email uniqueness.
- It does not require DNS or custom domain work.
- It can coexist with the current email-only login during migration.

Future enhancement:

```text
Option C: Subdomain Based Login
```

Subdomain login can be added after organization onboarding is stable.

## Non-Goals For Sprint 8

- No login payload changes.
- No auth endpoint changes.
- No subdomain routing.
- No custom domain routing.

