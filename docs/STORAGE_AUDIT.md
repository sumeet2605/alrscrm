# Storage Audit

Audit date: 2026-06-12

## Scope

Repository-wide audit of DigitalOcean Spaces integration, Gallery storage,
Delivery artifact storage, Finance PDF handling, file access patterns, CDN
compatibility, versioning behavior, and UAT readiness.

No application code or migrations were changed.

## Summary Verdict

| Area | Verdict |
| --- | --- |
| Private Spaces bucket with presigned URLs | SAFE with `DO_SPACES_CDN_URL` unset |
| Spaces versioning | SAFE TO ENABLE |
| Spaces CDN | NOT SAFE TO ENABLE with current protected-media model |
| UAT with CDN enabled | REQUIRES CHANGES BEFORE UAT |
| UAT without CDN, private bucket, presigned URLs | Acceptable after real bucket smoke test |

## Storage Provider Architecture

The active storage abstraction is in `backend/app/galleries/storage/provider.py`.
Despite the module path, Delivery uses the same provider.

### Providers

- `LocalMetadataStorageProvider`
  - Stores uploaded content as data URLs for local/test metadata behavior.
  - Returns `local://...` or data URLs directly.
- `DigitalOceanSpacesStorageProvider`
  - Uses `boto3.client("s3")`.
  - Uploads objects with `ACL: private`.
  - Stores object keys, not full Spaces URLs.
  - Deletes by object key.
  - Generates presigned `get_object` URLs unless `DO_SPACES_CDN_URL` is set.

### Uploads

Gallery multipart upload:

- Route: `POST /api/v1/galleries/{gallery_id}/photos/upload`
- Service method: `upload_photo_file(...)`
- Object key shape:

```text
{DO_SPACES_PATH_PREFIX}/{organization_id}/{branch_id}/{gallery_id}/{file_name}
```

Delivery ZIP generation:

- Route: `POST /api/v1/delivery/jobs/{job_id}/generate-zip`
- Service method: `generate_zip(...)`
- Object key shape:

```text
{DO_SPACES_PATH_PREFIX}/{organization_id}/{branch_id}/delivery/{delivery_job_id}/{delivery_number}.zip
```

Manual gallery photo registration:

- Route: `POST /api/v1/galleries/{gallery_id}/photos`
- Accepts `storage_path` and `thumbnail_path` from the API payload.
- Calls `generate_signed_url(storage_path)` but does not verify object
  ownership, object existence, or key prefix containment. With S3-style
  presigning, this does not prove the object exists.

## Gallery Images

### Current Behavior

Gallery photos are stored in `gallery_photos.storage_path` and optional
`gallery_photos.thumbnail_path`.

When a Gallery detail response is built, backend replaces:

- `storage_path` with `storage_provider.generate_signed_url(item.storage_path)`
- `thumbnail_path` with `storage_provider.generate_thumbnail_url(item.thumbnail_path)`

The frontend uses:

```text
photo.thumbnail_path ?? photo.storage_path
```

as the image source in staff and public Gallery screens.

### Public Accessibility

Gallery images are accessible through application-mediated Gallery APIs:

- Staff routes require `galleries:*` permissions and tenant/branch scope checks.
- Public client routes require an opaque Gallery access token.
- Password-protected galleries require a temporary Gallery session token.
- Gallery access tokens expire at the Gallery expiry or default to 90 days.
- Gallery password session tokens expire after 2 hours.

### Originals And Thumbnails

With Spaces provider:

- Originals and thumbnails currently use the same object key for multipart
  upload because `upload_file()` returns `thumbnail_path=key`.
- Both are private at upload time because `put_object` uses `ACL: private`.
- Both are returned as presigned URLs when `DO_SPACES_CDN_URL` is unset.
- Both are returned as non-expiring CDN URLs when `DO_SPACES_CDN_URL` is set.

### Gallery Risks

1. CDN URL mode bypasses signed URL expiry.
2. Manual photo registration can store arbitrary object keys supplied by a user
   with `galleries:photos:write`.
3. Public Gallery client access receives rendered image URLs. If those URLs are
   CDN URLs, access outlives Gallery token expiry and password/session expiry.
4. The old UUID public Gallery routes still exist in code, but tests assert UUID
   public access is rejected.

## Delivery Files

### Current Behavior

Delivery ZIP artifacts are created by `generate_zip(...)`.

The generated ZIP is currently a manifest-only ZIP, not a package of actual
edited image binaries. This is a functional limitation, not a Spaces-specific
security issue.

Delivery artifacts are stored in `delivery_artifacts.storage_key`; the database
stores object keys, not bucket URLs.

### Public Accessibility

Public Delivery uses layered access:

1. Client link contains an opaque raw Delivery access token.
2. Raw token is hashed in storage.
3. Optional Delivery password can be required.
4. `POST /api/v1/delivery/public/authenticate` creates a temporary delivery
   session token.
5. `POST /api/v1/delivery/client/{token}/download` requires the delivery session
   bearer token.
6. Backend increments download audit/count and returns `download_url`.

### Signed URL Behavior

When `DO_SPACES_CDN_URL` is unset:

- `download_url` is a Spaces presigned URL.
- Expiry is controlled by `STORAGE_SIGNED_URL_EXPIRE_SECONDS`, default `900`.

When `DO_SPACES_CDN_URL` is set:

- `download_url` is a CDN URL.
- It has no application-enforced expiry.
- Download limits still prevent new URL generation, but any already returned CDN
  URL may remain usable outside the application.

## Finance Documents

Finance documents do not currently use Spaces.

Invoice PDFs:

- Route: `GET /api/v1/invoices/{invoice_id}/pdf`
- Requires `finance:view`.
- Generated in memory by `invoice_pdf(item)`.
- Returned directly as `application/pdf`.

Payment receipts:

- Route: `GET /api/v1/payments/{payment_id}/receipt`
- Requires `finance:view`.
- Generated in memory by `payment_receipt_pdf(item)`.
- Returned directly as `application/pdf`.

No invoice PDF or payment receipt object key is stored in the database.
No public URL is generated for Finance documents.

## CDN Compatibility

Current CDN compatibility status: NOT READY for protected media.

The provider has this behavior:

```text
if DO_SPACES_CDN_URL is set:
    return "{cdn_url}/{quoted_object_key}"
else:
    return boto3.generate_presigned_url(...)
```

This means CDN mode changes the security semantics of every generated media URL:

- Gallery original URLs become CDN URLs.
- Gallery thumbnail URLs become CDN URLs.
- Delivery ZIP download URLs become CDN URLs.
- `STORAGE_SIGNED_URL_EXPIRE_SECONDS` is ignored.

If the CDN is public, it bypasses application token expiry, password sessions,
Delivery download counts after URL generation, and revocation after URL
issuance. If the bucket remains private and the CDN cannot read private objects
without an origin access/private-signing mechanism, CDN URLs may simply fail.

## Versioning Compatibility

Spaces versioning appears safe to enable.

The application stores object keys only and does not store version IDs.
Reads always target the latest version for a key.

Observed behavior:

- Gallery upload creates a key; duplicate keys are constrained per Gallery by
  `uq_gallery_photo_storage_path`.
- Gallery delete calls `delete_object` and marks the DB row inactive.
- Delivery regeneration can upload to the same deterministic ZIP key and creates
  another `delivery_artifacts` row with the same key and new timestamp.
- Delivery downloads use the latest artifact row by `generated_at`, but object
  reads still fetch latest object version for that key.

Versioning impact:

- Delete operations create delete markers rather than permanently removing
  historical bytes.
- Restore can recover accidentally deleted/overwritten objects.
- Storage cost may grow without lifecycle rules.

## Environment Configuration

Supported by code and `.env.example`:

- `DO_SPACES_BUCKET`
- `DO_SPACES_REGION`
- `DO_SPACES_ENDPOINT_URL`
- `DO_SPACES_CDN_URL`
- `DO_SPACES_ACCESS_KEY`
- `DO_SPACES_SECRET_KEY`
- `DO_SPACES_PATH_PREFIX`
- `STORAGE_SIGNED_URL_EXPIRE_SECONDS`

Not supported exactly as named:

- `DO_SPACES_ENDPOINT`

The code uses `DO_SPACES_ENDPOINT_URL`; setting only `DO_SPACES_ENDPOINT` has no
effect.

## Readiness Check

When Spaces provider is active, `/health/ready` calls `head_bucket` against the
configured bucket. This verifies basic credential and bucket reachability, but
does not verify upload, delete, presigned URL generation, CDN behavior, object
versioning, or private/public policy behavior.

## Required Follow-Up Before CDN UAT

1. Do not set `DO_SPACES_CDN_URL` for protected media until CDN access is
   explicitly private, signed, or proxied.
2. Decide whether Gallery thumbnails can be public. If yes, separate thumbnail
   and original storage policies. If no, keep thumbnails presigned too.
3. Prevent manual `storage_path` registration from referencing arbitrary object
   keys, or validate key prefix ownership and object existence.
4. Add an integration smoke test against a real private Spaces bucket:
   upload -> read via presigned URL -> deny unauthenticated origin URL -> delete
   -> verify behavior with versioning.
5. Add a CDN-specific test before enabling CDN:
   private object cannot be fetched after app token expiry or revocation unless
   the app issues a fresh authorized URL.

