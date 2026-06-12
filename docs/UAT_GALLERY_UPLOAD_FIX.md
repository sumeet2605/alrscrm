# UAT Gallery Upload Fix

## Fix Summary

The gallery upload contract is now locked to the canonical backend field name and backward compatible with legacy clients.

Changes:

- Frontend upload now passes the real browser `File` object, unwrapping Ant Design's `originFileObj` when needed.
- Shared Axios client no longer applies a global `Content-Type: application/json` header, allowing browser FormData requests to be sent as `multipart/form-data` with the required boundary.
- Gallery upload uses a client-side queue for large batches while keeping the backend one-file-per-request architecture.
- Queue concurrency is capped at 5 active uploads.
- Each file is retried up to 3 attempts; failed files do not stop the remaining queue.
- The upload page shows per-file progress and overall batch progress for multi-select uploads, including 250+ photo batches.
- Frontend regression test added to assert `uploadGalleryPhoto` sends the image as multipart field `file`.
- Frontend regression test added to ensure FormData requests do not retain the JSON content type.
- Backend upload endpoint continues to use `file` as the canonical multipart field.
- Backend now also accepts legacy multipart field `photo` as a fallback, preventing older deployed clients from failing with `body.file` missing.
- Backend regression tests cover canonical upload behavior, legacy field compatibility, gallery visibility after upload, and Spaces-style storage provider integration.

## Contract

Endpoint:

`POST /api/v1/galleries/{gallery_id}/photos/upload`

Canonical multipart body:

```text
file: image file
image_width: positive integer
image_height: positive integer
sort_order: optional integer
```

Backward-compatible alias:

```text
photo: image file
```

If both `file` and `photo` are sent, `file` takes precedence.

## Verification

Automated coverage added:

- `backend/tests/test_galleries_api.py`
  - Canonical `file` upload returns a renderable URL.
  - Legacy `photo` upload succeeds.
  - Spaces-style provider receives bytes, content type, object key, and returns signed URLs.
  - Uploaded image appears in the gallery detail response.
- `frontend/src/api/galleries.test.ts`
  - `uploadGalleryPhoto` appends the browser `File` object under `file`.
  - The legacy `photo` field is not emitted by the frontend helper.
  - Ant Design upload wrapper objects are unwrapped before FormData is built.
- `frontend/src/api/http.test.ts`
  - FormData requests are not serialized as JSON and do not retain the JSON content type.
- `frontend/src/modules/bookings/GalleryUploadPage.test.tsx`
  - Multiple selected files are uploaded through the queue with at most 5 concurrent API calls.
  - Failed uploads are retried while the remaining queue continues.
  - Per-file and overall progress UI is rendered.

Manual browser verification:

1. Open a gallery upload page at `/galleries/{gallery_id}/upload`.
2. Upload a JPEG or PNG.
3. Confirm the browser network request uses `multipart/form-data` and the payload contains multipart field `file`.
4. Confirm the API returns `201`.
5. Confirm the image appears in the gallery photo table and gallery detail view.
6. Repeat with 10, 100, and 250 images; confirm only 5 requests are active at a time and failed files retry without blocking the rest.

DigitalOcean Spaces verification:

1. Run with `STORAGE_PROVIDER=spaces` or `STORAGE_PROVIDER=digitalocean`.
2. Configure `DO_SPACES_REGION`, `DO_SPACES_BUCKET`, `DO_SPACES_ACCESS_KEY`, `DO_SPACES_SECRET_KEY`, and optional CDN settings.
3. Upload from the browser.
4. Confirm the API response contains signed or CDN URLs.
5. Confirm the object key exists in Spaces under the configured path prefix.
