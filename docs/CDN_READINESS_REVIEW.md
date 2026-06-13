# CDN Readiness Review

Audit date: 2026-06-12

## Verdict

A. SAFE TO ENABLE CDN NOW: NO

ALRSCRM should not enable `DO_SPACES_CDN_URL` for UAT protected media with the
current implementation.

## Why CDN Is Not Ready

The DigitalOcean Spaces provider treats CDN configuration as a replacement for
presigned URLs:

```text
generate_signed_url(key)
  -> returns DO_SPACES_CDN_URL/key when DO_SPACES_CDN_URL is configured
  -> otherwise returns boto3 generate_presigned_url(...)
```

That means a setting intended to improve delivery performance changes access
control behavior.

## Affected Surfaces

### Gallery

Staff and public Gallery detail responses include photo URL fields:

- `storage_path`
- `thumbnail_path`

The backend rewrites both fields into generated URLs before returning responses.
The frontend renders `thumbnail_path ?? storage_path` directly as an image `src`.

With CDN enabled, public Gallery clients receive CDN URLs for thumbnails and
original images. Those URLs are not tied to:

- Gallery access token expiry.
- Gallery token revocation.
- Gallery password session expiry.
- Gallery expiration.

### Delivery

Public Delivery downloads are currently protected before URL generation:

- Opaque Delivery token.
- Optional password.
- Temporary delivery session token.
- Download limit and audit record.

With CDN enabled, the returned `download_url` is not a temporary presigned URL.
The app can stop issuing new URLs, but it cannot expire a CDN URL already handed
to the browser unless the CDN itself has private/signed access controls.

### Finance

Finance PDFs and receipts are not CDN-backed today. They are generated in memory
behind authenticated `finance:view` routes and downloaded as blobs.

## Hardcoded Origin URL Review

No hardcoded DigitalOcean origin URL was found in application code. The provider
constructs a default endpoint from region:

```text
https://{region}.digitaloceanspaces.com
```

when `DO_SPACES_ENDPOINT_URL` is absent.

Stored database values are object keys such as:

```text
{prefix}/{organization_id}/{branch_id}/{gallery_id}/{file_name}
{prefix}/{organization_id}/{branch_id}/delivery/{delivery_job_id}/{delivery_number}.zip
```

not origin URLs.

## Private Bucket + CDN Risk

The code does not implement a private CDN signing mechanism.

Possible outcomes if CDN is enabled:

- If CDN access is public, protected media becomes available through non-expiring
  CDN URLs after the app discloses them once.
- If the bucket is private and the CDN cannot read it, image and ZIP URLs may
  fail.
- If the CDN caches an object after authorization, later app-side revocation may
  not revoke the cached URL.

## CDN Cache Invalidation Risk

The app has no CDN purge/invalidation integration.

This matters for:

- Gallery photo deletion.
- Gallery access token revocation.
- Gallery expiry.
- Delivery access token revocation.
- Delivery expiry.
- Delivery ZIP regeneration at the same key.

## Recommended CDN Path

Before enabling CDN, implement one of these models:

1. Keep bucket private and keep returning Spaces presigned URLs. Leave
   `DO_SPACES_CDN_URL` unset.
2. Use app-proxied media downloads and stream private objects through the API
   after authorization.
3. Use a CDN with private signed URLs/cookies and short TTLs, generated only
   after app authorization.
4. Split storage classes:
   - Public derivatives only, such as watermarked thumbnails.
   - Private originals and ZIPs through presigned URLs only.

## CDN UAT Decision

Do not enable Spaces CDN for current UAT unless the UAT explicitly accepts that
media URLs returned to clients may be non-expiring public CDN URLs.

For normal UAT privacy expectations, leave:

```text
DO_SPACES_CDN_URL=
```

