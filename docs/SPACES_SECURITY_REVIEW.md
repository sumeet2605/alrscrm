# Spaces Security Review

Audit date: 2026-06-12

## Verdicts

| Question | Verdict |
| --- | --- |
| A. Safe to enable CDN now | NO |
| B. Safe to enable versioning now | YES |
| C. Safe to keep bucket private | YES, with `DO_SPACES_CDN_URL` unset |
| D. Requires changes before UAT | YES if UAT requires CDN; otherwise operational Spaces smoke testing is still required |

## Security Model

The safest current ALRSCRM Spaces configuration is:

```text
STORAGE_PROVIDER=spaces
DO_SPACES_BUCKET=<private-bucket>
DO_SPACES_REGION=<region>
DO_SPACES_ENDPOINT_URL=https://<region>.digitaloceanspaces.com
DO_SPACES_CDN_URL=
STORAGE_SIGNED_URL_EXPIRE_SECONDS=900
DO_SPACES_PATH_PREFIX=alrscrm/uat
```

This keeps objects private and causes the backend to generate presigned URLs
when images or Delivery ZIPs need to be accessed.

## Object URL Exposure

### Database

The database stores object keys, not full public URLs:

- `gallery_photos.storage_path`
- `gallery_photos.thumbnail_path`
- `delivery_artifacts.storage_key`

Delivery client access URLs are application routes:

```text
/client/delivery/{token}
```

Gallery client access URLs are application routes:

```text
/client/gallery/{token}
```

### API Responses

The backend does expose generated object access URLs in API responses:

- Gallery staff detail responses.
- Gallery public client responses.
- Delivery public download response.

This is expected for media rendering and downloads, but the URL must remain
temporary. It is temporary only when `DO_SPACES_CDN_URL` is unset.

## Bucket Privacy

The Spaces upload path sets `ACL: private` on `put_object`. This supports a
private bucket model.

Private bucket readiness is still not fully proven by automated tests because
the current test suite uses local metadata storage, not a real Spaces bucket.
`/health/ready` confirms `head_bucket`, but not private URL denial or presigned
URL success.

## Signed URL Downloads

Signed URL behavior is present when CDN URL is not configured.

Default expiry:

```text
STORAGE_SIGNED_URL_EXPIRE_SECONDS=900
```

Affected resources:

- Gallery originals.
- Gallery thumbnails.
- Delivery ZIP artifacts.

Finance PDFs are not signed URLs; they are authenticated API responses.

## Tenant Isolation Review

### Strong Points

- Multipart Gallery uploads generate keys containing organization, branch, and
  gallery IDs.
- Delivery ZIP keys contain organization, branch, and delivery job IDs.
- Staff Gallery, Delivery, and Finance routes enforce tenant/branch scope.
- Public Gallery and Delivery use opaque access tokens rather than raw IDs.
- Delivery downloads require a temporary session token before URL generation.

### Risks

1. Manual Gallery photo registration accepts arbitrary `storage_path` and
   `thumbnail_path`.
   - A user with `galleries:photos:write` could register a known object key from
     another tenant if they can guess or obtain it.
   - The provider will generate a signed URL for that key without checking
     prefix ownership.
2. CDN URL mode removes app-controlled URL expiry.
3. Delivery artifact schemas expose `storage_key` to staff Delivery responses.
   This is not a direct URL, but it reveals bucket key structure to users with
   Delivery access.
4. Delivery ZIP generation currently produces a manifest-only ZIP, so UAT should
   not claim final edited image packaging is complete.

## Files Accessible Without Authorization

With `DO_SPACES_CDN_URL` unset and bucket private:

- Direct object access should require a presigned URL.
- Presigned URLs are only returned after app route authorization or public token
  validation.

With `DO_SPACES_CDN_URL` set:

- Any object URL returned once may be accessible without later app
  authorization, depending on CDN/bucket policy.

Finance PDFs and receipts are not accessible without authenticated
`finance:view` route access.

## Versioning Review

Spaces versioning is safe to enable.

Reasons:

- The app does not store version IDs.
- Reads naturally use the latest object version.
- Deletes do not assume permanent erase.
- Overwrites are limited by deterministic delivery ZIP keys and Gallery unique
  key constraints.

Operational requirements:

- Configure lifecycle retention for old object versions.
- Document restore procedure for a single object prefix.
- Verify delete-marker behavior during restore drills.

## CDN Review

CDN is not safe to enable today for protected media.

The current `DO_SPACES_CDN_URL` implementation creates a public URL by string
joining the CDN base URL and object key. It does not:

- Sign CDN URLs.
- Set CDN TTL per URL.
- Validate caller authorization at CDN edge.
- Purge CDN objects on token revocation, Gallery expiry, or Delivery expiry.
- Preserve `STORAGE_SIGNED_URL_EXPIRE_SECONDS`.

## Environment Configuration Review

Supported:

- `DO_SPACES_BUCKET`
- `DO_SPACES_REGION`
- `DO_SPACES_ENDPOINT_URL`
- `DO_SPACES_CDN_URL`

Not supported by the current settings model:

- `DO_SPACES_ENDPOINT`

The requested `DO_SPACES_ENDPOINT` name should either be documented as
unsupported or added as an alias in a future code change. For now, use
`DO_SPACES_ENDPOINT_URL`.

## UAT Readiness Checklist

Required before using Spaces in UAT:

- [ ] Use a private Space.
- [ ] Keep `DO_SPACES_CDN_URL` unset.
- [ ] Set a UAT-specific `DO_SPACES_PATH_PREFIX`.
- [ ] Verify `/health/ready` returns `storage.ok=true`.
- [ ] Upload a Gallery image through multipart upload.
- [ ] Confirm the stored object has private ACL.
- [ ] Confirm direct origin URL without signature is denied.
- [ ] Confirm generated Gallery image URL works before expiry.
- [ ] Confirm generated Gallery image URL fails after expiry.
- [ ] Generate a Delivery ZIP and confirm download URL works before expiry.
- [ ] Confirm Delivery download URL fails after expiry.
- [ ] Enable Spaces versioning.
- [ ] Perform one object restore drill.

## Final UAT Position

Use DigitalOcean Spaces for UAT only in private-bucket, presigned-URL mode.

Do not enable Spaces CDN for protected Gallery images, thumbnails, or Delivery
ZIPs until CDN access control is redesigned and tested.

