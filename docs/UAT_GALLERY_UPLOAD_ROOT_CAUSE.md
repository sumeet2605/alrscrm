# UAT Gallery Upload Root Cause

## Symptom

`POST /api/v1/galleries/{gallery_id}/photos/upload` failed in UAT with:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "file"],
      "msg": "Field required"
    }
  ]
}
```

## Investigation

Backend upload endpoint:

- File: `backend/app/galleries/routes.py`
- Route: `POST /api/v1/galleries/{gallery_id}/photos/upload`
- Canonical multipart file field: `file`
- Required form fields accepted by the endpoint: `image_width`, `image_height`, optional `sort_order`

Required grep findings:

- `UploadFile` usage in gallery routes resolves to `upload_gallery_photo`.
- `FormData` usage in gallery frontend resolves to `frontend/src/api/galleries.ts`.

Frontend upload implementation:

- File: `frontend/src/api/galleries.ts`
- Function: `uploadGalleryPhoto`
- Canonical field after the fix: `formData.append("file", file)`
- Shared HTTP client: `frontend/src/api/http.ts`
- Confirmed broken UAT request: `Content-Type: application/json`

Broken UAT payload:

```json
{
  "file": {
    "uid": "..."
  },
  "image_width": "...",
  "image_height": "..."
}
```

## Root Cause

The backend contract required a multipart file part named `file`. UAT traffic sent JSON instead of `multipart/form-data`; the `file` value was an Ant Design upload wrapper object, not the browser `File` binary.

FastAPI never received an `UploadFile`, so validation failed before application code ran and returned the missing `body.file` validation error.

This was a request encoding contract mismatch, not a storage failure.

## Storage Impact

Because validation failed before `gallery_service.upload_photo_file` was called, the upload never reached the storage provider. No object was written to DigitalOcean Spaces for the failed requests.
