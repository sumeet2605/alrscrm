# UAT Spaces Upload Root Cause

## Symptom

Gallery upload now reaches the backend, then fails during object storage upload:

```text
botocore.exceptions.ClientError:
An error occurred (InvalidArgument) when calling the PutObject operation
```

The same Spaces compatibility issue also appeared when deleting a gallery photo:

```text
botocore.exceptions.ClientError:
An error occurred (InvalidArgument) when calling the DeleteObject operation
```

Failure path:

```text
backend/app/galleries/routes.py
-> gallery_service.upload_photo_file()
-> storage_provider.upload_file()
-> boto3 client.put_object()
```

## Request Inspection

Provider file:

`backend/app/galleries/storage/provider.py`

Previous explicit `put_object` arguments:

```text
Bucket=<DO_SPACES_BUCKET>
Key=<DO_SPACES_PATH_PREFIX>/<organization_id>/<branch_id>/<gallery_id>/<file_name>
Body=<uploaded bytes>
ContentType=<browser content type>
ACL=private
Metadata=None
CacheControl=None
ExtraArgs=None
```

The explicit arguments were simple, but the installed `botocore` version can add
automatic checksum request behavior for S3 operations. DigitalOcean Spaces is
S3-compatible, but not every AWS S3 SDK extension/header is accepted by Spaces.
That hidden SDK-level request behavior can surface as `InvalidArgument` on
`PutObject`.

## Root Cause

The Spaces provider was not pinned to the minimal S3-compatible request shape.
It also sent an unnecessary object ACL. For a private Space, privacy should be
controlled by the Space/bucket policy and credentials, not by setting an object
ACL on every upload.

The fixed upload request is:

```text
Bucket=<DO_SPACES_BUCKET>
Key=<DO_SPACES_PATH_PREFIX>/<organization_id>/<branch_id>/<gallery_id>/<file_name>
Body=<uploaded bytes>
ContentType=<browser content type, when provided>
ACL=None
Metadata=None
CacheControl=None
ExtraArgs=[]
```

The boto client is also configured with:

```text
request_checksum_calculation=when_required
response_checksum_validation=when_required
```

This prevents botocore from adding optional checksum behavior for Spaces uploads
unless it is required.

The provider also uses path-style S3 addressing for DigitalOcean Spaces:

```text
s3.addressing_style=path
```

If Spaces still rejects `PutObject` with optional `ContentType`, the provider
logs the failure and retries once with the absolute minimum request:

```text
Bucket
Key
Body
```

`DeleteObject` failures are logged but no longer block gallery record deletion,
because delete should not make the gallery UI unusable when an object is already
missing or Spaces rejects the delete request.

## Environment Checks

The UAT backend env file must contain:

```text
STORAGE_PROVIDER=spaces
DO_SPACES_REGION=sgp1
DO_SPACES_BUCKET=alrscrm-uat
DO_SPACES_ACCESS_KEY=<rotated-access-key>
DO_SPACES_SECRET_KEY=<rotated-secret-key>
DO_SPACES_ENDPOINT_URL=https://sgp1.digitaloceanspaces.com
DO_SPACES_CDN_URL=
DO_SPACES_PATH_PREFIX=alrscrm
```

`/health/ready` verifies bucket access with `head_bucket` when Spaces storage is
active.
