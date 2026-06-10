# Gallery Event Map

ALRSCRM still uses audit-backed domain events. Sprint 5 does not introduce an
outbox, message bus, or asynchronous handlers.

## Implemented Audit Events

| Event | Domain Event | Owner | Trigger |
| --- | --- | --- | --- |
| `gallery.created` | `GalleryCreated` | Gallery | Gallery created for a BookingItem. |
| `gallery.updated` | `GalleryUpdated` | Gallery | Gallery metadata updated. |
| `gallery.status_changed` | `GalleryStatusChanged` | Gallery | Gallery status changed. |
| `gallery.photo_uploaded` | `GalleryPhotoUploaded` | Gallery | Photo metadata added to a Gallery. |
| `gallery.photo_deleted` | `GalleryPhotoDeleted` | Gallery | Photo soft-deleted from a Gallery. |
| `gallery.favorite_selected` | `FavoriteSelected` | Gallery | Client or staff favorite selection saved. |

## Not Implemented

- Editing events
- Delivery events
- Payment events
- Outbox publication events

## Ownership Rules

- Gallery owns photo upload and favorite selection events.
- Booking remains the owner of booking and scheduling events.
- Gallery events reference BookingItem but do not mutate Booking state.
