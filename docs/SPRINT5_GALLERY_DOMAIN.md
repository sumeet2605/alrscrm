# Sprint 5 Gallery Domain

Sprint 5 introduces Gallery Management and Client Photo Selection.

Implemented scope:

- Photos uploaded
- Client favorite selection
- Gallery metrics

Not implemented:

- Editing
- Final delivery
- Payments

## Aggregate Boundary

`Gallery` is the aggregate root for client photo selection.

`Gallery` references:

- `organization_id`
- `branch_id`
- `booking_id`
- `booking_item_id`
- `created_by_user_id`

`Gallery` owns:

- `GalleryPhoto`
- `FavoriteSelection`
- Gallery status
- Expiry and optional password hash

`Gallery` does not duplicate Family customer profile data. Read APIs may return
booking number and family name for display, but those values are derived through
the Booking and Family references.

## Booking Item Ownership

Gallery is owned by `BookingItem`.

One Booking may have many BookingItems, and each BookingItem can have one
Gallery.

```text
Booking
  BookingItem
    Gallery
      GalleryPhoto
      FavoriteSelection
```

## Statuses

- `DRAFT`
- `UPLOADED`
- `SELECTION_OPEN`
- `SELECTION_CLOSED`

## Business Rules

- Gallery creation requires an existing Booking and BookingItem.
- BookingItem must belong to the selected Booking.
- Gallery inherits organization and branch scope from Booking.
- Photos cannot be added after selection is closed.
- Photos cannot be deleted after selection is closed.
- Favorites can be added only when selection is open.
- Public client selection does not grant CRM access.

## Storage

Sprint 5 introduces `StorageProvider` with:

- `upload_file()`
- `delete_file()`
- `generate_signed_url()`
- `generate_thumbnail_url()`

The current implementation uses a local metadata provider and stores file paths
from the API payload. Cloud providers are intentionally not hardcoded.

Production storage can use DigitalOcean Spaces through the S3-compatible
`DigitalOceanSpacesStorageProvider`.

Required environment:

- `STORAGE_PROVIDER=digitalocean`
- `DO_SPACES_REGION`
- `DO_SPACES_BUCKET`
- `DO_SPACES_ACCESS_KEY`
- `DO_SPACES_SECRET_KEY`

Optional environment:

- `DO_SPACES_ENDPOINT_URL`
- `DO_SPACES_CDN_URL`
- `DO_SPACES_PATH_PREFIX`
- `STORAGE_SIGNED_URL_EXPIRE_SECONDS`

When `DO_SPACES_CDN_URL` is set, gallery reads return CDN URLs. Otherwise,
gallery reads return presigned Spaces URLs.

The frontend upload flow uses `POST /api/v1/galleries/{id}/photos/upload` with
multipart form data. The older JSON metadata endpoint remains available for
backwards-compatible integrations.

## Metrics

`GET /api/v1/galleries/metrics` returns:

- Total Galleries
- Photos Uploaded
- Selection Open Galleries
- Selection Closed Galleries
- Favorite Count

Metrics are scoped by the caller's tenant and branch permissions.
