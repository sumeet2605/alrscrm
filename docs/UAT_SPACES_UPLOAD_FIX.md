# UAT Spaces Upload Fix

## Fix Summary

The DigitalOcean Spaces provider now uses a minimal S3-compatible `PutObject`
request and disables optional botocore checksum behavior unless required.

Changed file:

`backend/app/galleries/storage/provider.py`

Upload behavior after the fix:

```text
Bucket=<configured bucket>
Key=<prefix>/<organization_id>/<branch_id>/<gallery_id>/<file_name>
Body=<uploaded bytes>
ContentType=<uploaded file content type, when present>
ACL=None
Metadata=None
CacheControl=None
ExtraArgs=[]
```

No object ACL is sent. Private bucket behavior is controlled by the Space and
access credentials.

## Logging

The provider logs sanitized `PutObject` details before upload:

```text
Bucket
Key
ContentType
ACL
Metadata
CacheControl
ExtraArgs
BodyBytes
```

Secrets and file bytes are not logged.

## Regression Tests

Added:

`backend/tests/test_spaces_storage_provider.py`

Coverage:

- Spaces client uses `request_checksum_calculation=when_required`.
- Spaces client uses `response_checksum_validation=when_required`.
- Upload calls `put_object` with only `Bucket`, `Key`, `Body`, and optional
  `ContentType`.
- Upload does not send `ACL`, `Metadata`, or `CacheControl`.
- Sanitized request logging includes the expected argument summary.

Existing gallery upload tests continue to verify:

- Multipart upload creates a gallery record.
- Stored image URL is returned through the storage provider.
- Gallery detail includes the uploaded photo.

## UAT Verification

On the droplet:

```bash
docker compose exec -T api python - <<'PY'
from app.core.config import get_settings
from app.galleries.storage import get_storage_provider

s = get_settings()
p = get_storage_provider()
print(s.storage_provider, s.do_spaces_bucket, s.do_spaces_region, s.do_spaces_endpoint_url)
print(type(p).__name__)
PY
```

Expected:

```text
spaces alrscrm-uat sgp1 https://sgp1.digitaloceanspaces.com
DigitalOceanSpacesStorageProvider
```

Minimal Spaces write test:

```bash
docker compose exec -T api python - <<'PY'
from app.galleries.storage import get_storage_provider

p = get_storage_provider()
p.client.put_object(
    Bucket=p.bucket,
    Key=f"{p.path_prefix}/diagnostics/minimal-put-object.txt",
    Body=b"ok",
)
print("minimal put_object ok")
PY
```

Application upload verification:

1. Upload one image from the browser gallery upload page.
2. Confirm API returns `201`.
3. Confirm `gallery_photos` has a row for the image.
4. Confirm the object key exists in Space `alrscrm-uat` under `alrscrm/...`.
5. Open the returned gallery preview URL and confirm it renders.
