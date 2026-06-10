# Sprint 5 Completion Report

Sprint 5 implements Gallery Management and Client Photo Selection.

## Implemented Scope

- Gallery aggregate rooted at `Gallery`
- `GalleryPhoto` child entity
- `FavoriteSelection` child entity
- Public client selection view
- Gallery metrics
- Storage provider abstraction
- DigitalOcean Spaces storage provider
- Audit-backed gallery event vocabulary

Not implemented:

- Editing
- Final delivery
- Payments

## Backend Files Created

- `backend/app/galleries/enums.py`
- `backend/app/galleries/models/gallery.py`
- `backend/app/galleries/repositories.py`
- `backend/app/galleries/routes.py`
- `backend/app/galleries/schemas/gallery.py`
- `backend/app/galleries/services/gallery_service.py`
- `backend/app/galleries/storage/provider.py`
- `backend/alembic/versions/202606100009_create_gallery_management.py`
- `backend/tests/test_galleries_api.py`

## Frontend Files Created

- `frontend/src/api/galleries.ts`
- `frontend/src/types/galleries.ts`
- `frontend/src/modules/bookings/GalleryManagementPage.tsx`
- `frontend/src/modules/bookings/GalleryDetailsPage.tsx`
- `frontend/src/modules/bookings/GalleryUploadPage.tsx`
- `frontend/src/modules/bookings/ClientSelectionPage.tsx`
- `frontend/src/modules/bookings/galleryOptions.ts`
- `frontend/src/modules/bookings/GalleryManagementPage.test.tsx`
- `frontend/src/modules/bookings/ClientSelectionPage.test.tsx`

## Documentation Created

- `docs/SPRINT5_GALLERY_DOMAIN.md`
- `docs/GALLERY_AGGREGATE_DIAGRAM.md`
- `docs/GALLERY_EVENT_MAP.md`
- `docs/SPRINT5_COMPLETION_REPORT.md`

## Database Tables Added

- `galleries`
- `gallery_photos`
- `favorite_selections`

## APIs Added

- `GET /api/v1/galleries`
- `POST /api/v1/galleries`
- `GET /api/v1/galleries/metrics`
- `GET /api/v1/galleries/{id}`
- `PUT /api/v1/galleries/{id}`
- `GET /api/v1/galleries/{id}/photos`
- `POST /api/v1/galleries/{id}/photos`
- `POST /api/v1/galleries/{id}/photos/upload`
- `DELETE /api/v1/galleries/{id}/photos/{photo_id}`
- `GET /api/v1/galleries/{id}/favorites`
- `POST /api/v1/galleries/{id}/favorites`
- `DELETE /api/v1/galleries/{id}/favorites/{favorite_id}`
- `GET /api/v1/galleries/{id}/public`
- `POST /api/v1/galleries/{id}/public/favorites`
- `DELETE /api/v1/galleries/{id}/public/favorites/{favorite_id}`

## Frontend Routes Added

- `/galleries`
- `/galleries/:galleryId`
- `/galleries/:galleryId/upload`
- `/client/galleries/:galleryId`

## RBAC

- Super Admin, Owner, Organization Admin, and Branch Manager can create galleries.
- Photographer can upload photos.
- Customer Success can view and manage favorites.
- Client selection uses public gallery routes and does not access the CRM shell.

## Validation

- Gallery cannot be created without an existing Booking and BookingItem.
- BookingItem must belong to the selected Booking.
- Photos cannot be added or deleted when selection is closed.
- Favorites can only be selected while selection is open.
- Metrics are tenant and branch scoped.
- Multipart uploads are stored through `StorageProvider`.
- DigitalOcean Spaces returns CDN URLs when `DO_SPACES_CDN_URL` is configured,
  otherwise presigned URLs are returned.

## Tests Added

Backend:

- Gallery service creation
- Gallery repository metrics
- Gallery API workflow
- Photographer upload workflow
- Public client favorite workflow
- Gallery metrics workflow

Frontend:

- Gallery management list and create workflow
- Client favorite selection workflow
- Route permission coverage for public client links

## Verification

- Backend lint passed.
- Backend tests passed.
- Frontend TypeScript lint passed.
- Frontend tests passed.
- Frontend build passed.

## Future Sprint Impacts

- Editing should reference selected GalleryPhoto or FavoriteSelection output.
- Delivery should reference Gallery or future edited deliverables.
- Payment should remain separate and should not be introduced into Gallery.
- A cloud storage provider can be added behind `StorageProvider`.
- A future outbox should replace audit-backed events for asynchronous workflows.
