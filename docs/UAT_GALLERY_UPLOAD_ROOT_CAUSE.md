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

## Root Cause

The backend contract required a multipart file part named `file`. UAT traffic sent the upload under a different multipart field name, so FastAPI rejected the request before application code ran and returned the missing `body.file` validation error.

This was a contract mismatch at the multipart boundary, not a storage failure.

## Storage Impact

Because validation failed before `gallery_service.upload_photo_file` was called, the upload never reached the storage provider. No object was written to DigitalOcean Spaces for the failed requests.
