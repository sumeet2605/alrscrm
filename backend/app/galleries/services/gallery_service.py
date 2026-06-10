from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.bookings.models import Booking, BookingItem
from app.core.security import hash_password
from app.galleries.enums import GalleryStatus
from app.galleries.models import FavoriteSelection, Gallery, GalleryPhoto
from app.galleries.repositories import GalleryRepository
from app.galleries.schemas.gallery import (
    FavoriteSelectionCreate,
    GalleryCreate,
    GalleryPhotoCreate,
    GalleryUpdate,
)
from app.galleries.storage import StorageProvider
from app.identity.policies import AuthorizationContext
from app.shared.exceptions.application import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event


def _scope_filters(
    context: AuthorizationContext, branch_id: UUID | None = None
) -> tuple[UUID | None, UUID | None]:
    if context.is_platform_admin:
        return None, branch_id
    scoped_branch_id = branch_id
    if context.is_branch_scoped:
        if branch_id is not None and branch_id != context.branch_id:
            raise ForbiddenError("Gallery branch is outside the caller scope")
        scoped_branch_id = context.branch_id
    return context.organization_id, scoped_branch_id


def _ensure_gallery_scope(context: AuthorizationContext, gallery: Gallery) -> None:
    if context.is_platform_admin:
        return
    if gallery.organization_id != context.organization_id:
        raise ForbiddenError("Gallery is outside the caller scope")
    if context.is_branch_scoped and gallery.branch_id != context.branch_id:
        raise ForbiddenError("Gallery is outside the caller scope")


def _ensure_booking_item_scope(
    context: AuthorizationContext, booking: Booking, booking_item: BookingItem
) -> None:
    if booking_item.booking_id != booking.id:
        raise ValidationError("Booking item must belong to booking")
    if not context.is_platform_admin:
        if booking.organization_id != context.organization_id:
            raise ForbiddenError("Booking is outside the caller scope")
        if context.is_branch_scoped and booking.branch_id != context.branch_id:
            raise ForbiddenError("Booking is outside the caller scope")


def _gallery_summary(gallery: Gallery) -> dict:
    active_photos = [photo for photo in gallery.photos if photo.is_active]
    return {
        "id": gallery.id,
        "organization_id": gallery.organization_id,
        "branch_id": gallery.branch_id,
        "booking_id": gallery.booking_id,
        "booking_item_id": gallery.booking_item_id,
        "gallery_name": gallery.gallery_name,
        "gallery_status": gallery.gallery_status,
        "created_by_user_id": gallery.created_by_user_id,
        "expires_at": gallery.expires_at,
        "created_at": gallery.created_at,
        "updated_at": gallery.updated_at,
        "booking_number": gallery.booking.booking_number if gallery.booking else None,
        "family_name": gallery.booking.family.primary_contact_name
        if gallery.booking and gallery.booking.family
        else None,
        "photo_count": len(active_photos),
        "favorite_count": len(gallery.favorites),
    }


def gallery_to_read(gallery: Gallery) -> dict:
    return _gallery_summary(gallery)


def gallery_to_detail(gallery: Gallery) -> dict:
    data = _gallery_summary(gallery)
    data["photos"] = [photo for photo in gallery.photos if photo.is_active]
    data["favorites"] = gallery.favorites
    return data


def list_galleries(
    db: Session,
    context: AuthorizationContext,
    *,
    page: int,
    page_size: int,
    branch_id: UUID | None = None,
    gallery_status: str | None = None,
    search: str | None = None,
) -> PageResult:
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    return GalleryRepository(db).list_galleries(
        page=page,
        page_size=page_size,
        organization_id=organization_id,
        branch_id=scoped_branch_id,
        gallery_status=gallery_status,
        search=search,
    )


def get_gallery(db: Session, gallery_id: UUID, context: AuthorizationContext) -> Gallery:
    gallery = GalleryRepository(db).get_gallery(gallery_id)
    if gallery is None:
        raise NotFoundError("Gallery not found")
    _ensure_gallery_scope(context, gallery)
    return gallery


def get_public_gallery(db: Session, gallery_id: UUID) -> Gallery:
    gallery = GalleryRepository(db).get_gallery(gallery_id)
    if gallery is None:
        raise NotFoundError("Gallery not found")
    if gallery.expires_at is not None and gallery.expires_at < datetime.now(UTC):
        raise ConflictError("Gallery link has expired")
    return gallery


def create_gallery(db: Session, payload: GalleryCreate, context: AuthorizationContext) -> Gallery:
    repository = GalleryRepository(db)
    booking_item = repository.booking_item_for_gallery(payload.booking_id, payload.booking_item_id)
    if booking_item is None:
        raise NotFoundError("Booking item not found")
    booking = booking_item.booking
    _ensure_booking_item_scope(context, booking, booking_item)
    gallery = Gallery(
        organization_id=booking.organization_id,
        branch_id=booking.branch_id,
        booking_id=booking.id,
        booking_item_id=booking_item.id,
        gallery_name=payload.gallery_name,
        gallery_status=payload.gallery_status.value,
        created_by_user_id=context.user_id,
        password_hash=hash_password(payload.password) if payload.password else None,
        expires_at=payload.expires_at,
    )
    repository.create_gallery(gallery)
    try:
        db.flush()
        record_audit_event(
            db,
            "gallery.created",
            context.user_id,
            "Gallery",
            gallery.id,
            metadata={"domain_event": "GalleryCreated"},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Gallery already exists for this booking item") from exc
    return get_gallery(db, gallery.id, context)


def update_gallery(
    db: Session, gallery_id: UUID, payload: GalleryUpdate, context: AuthorizationContext
) -> Gallery:
    repository = GalleryRepository(db)
    gallery = get_gallery(db, gallery_id, context)
    previous_status = gallery.gallery_status
    password_hash = hash_password(payload.password) if payload.password else None
    repository.update_gallery(gallery, payload, password_hash)
    event_name = "gallery.updated"
    domain_event = "GalleryUpdated"
    if payload.gallery_status is not None and payload.gallery_status.value != previous_status:
        event_name = "gallery.status_changed"
        domain_event = "GalleryStatusChanged"
    record_audit_event(
        db,
        event_name,
        context.user_id,
        "Gallery",
        gallery.id,
        metadata={"domain_event": domain_event},
    )
    db.commit()
    return get_gallery(db, gallery.id, context)


def list_photos(db: Session, gallery_id: UUID, context: AuthorizationContext) -> list[GalleryPhoto]:
    gallery = get_gallery(db, gallery_id, context)
    return [photo for photo in gallery.photos if photo.is_active]


def add_photo(
    db: Session,
    gallery_id: UUID,
    payload: GalleryPhotoCreate,
    context: AuthorizationContext,
    storage_provider: StorageProvider,
) -> GalleryPhoto:
    repository = GalleryRepository(db)
    gallery = get_gallery(db, gallery_id, context)
    if gallery.gallery_status == GalleryStatus.SELECTION_CLOSED.value:
        raise ConflictError("Cannot add photos after selection is closed")
    storage_provider.generate_signed_url(payload.storage_path)
    photo = repository.make_photo(
        gallery.id,
        file_name=payload.file_name,
        storage_path=payload.storage_path,
        thumbnail_path=payload.thumbnail_path,
        file_size=payload.file_size,
        image_width=payload.image_width,
        image_height=payload.image_height,
        sort_order=payload.sort_order or repository.next_photo_sort_order(gallery.id),
        is_active=payload.is_active,
    )
    repository.add_photo(photo)
    if gallery.gallery_status == GalleryStatus.DRAFT.value:
        gallery.gallery_status = GalleryStatus.UPLOADED.value
    record_audit_event(
        db,
        "gallery.photo_uploaded",
        context.user_id,
        "GalleryPhoto",
        photo.id,
        metadata={"domain_event": "GalleryPhotoUploaded", "gallery_id": str(gallery.id)},
    )
    db.commit()
    db.refresh(photo)
    return photo


def upload_photo_file(
    db: Session,
    gallery_id: UUID,
    *,
    file_name: str,
    content: bytes,
    content_type: str | None,
    image_width: int,
    image_height: int,
    sort_order: int,
    context: AuthorizationContext,
    storage_provider: StorageProvider,
) -> GalleryPhoto:
    repository = GalleryRepository(db)
    gallery = get_gallery(db, gallery_id, context)
    if gallery.gallery_status == GalleryStatus.SELECTION_CLOSED.value:
        raise ConflictError("Cannot add photos after selection is closed")
    stored_file = storage_provider.upload_file(
        f"{gallery.organization_id}/{gallery.branch_id}/{gallery.id}/{file_name}",
        content,
        content_type,
    )
    photo = repository.make_photo(
        gallery.id,
        file_name=file_name,
        storage_path=stored_file.storage_path,
        thumbnail_path=stored_file.thumbnail_path,
        file_size=stored_file.file_size,
        image_width=image_width,
        image_height=image_height,
        sort_order=sort_order or repository.next_photo_sort_order(gallery.id),
        is_active=True,
    )
    repository.add_photo(photo)
    if gallery.gallery_status == GalleryStatus.DRAFT.value:
        gallery.gallery_status = GalleryStatus.UPLOADED.value
    record_audit_event(
        db,
        "gallery.photo_uploaded",
        context.user_id,
        "GalleryPhoto",
        photo.id,
        metadata={"domain_event": "GalleryPhotoUploaded", "gallery_id": str(gallery.id)},
    )
    db.commit()
    db.refresh(photo)
    return photo


def delete_photo(
    db: Session,
    gallery_id: UUID,
    photo_id: UUID,
    context: AuthorizationContext,
    storage_provider: StorageProvider,
) -> None:
    gallery = get_gallery(db, gallery_id, context)
    if gallery.gallery_status == GalleryStatus.SELECTION_CLOSED.value:
        raise ConflictError("Cannot delete photos after selection is closed")
    photo = GalleryRepository(db).get_photo(photo_id)
    if photo is None or photo.gallery_id != gallery.id or not photo.is_active:
        raise NotFoundError("Photo not found")
    storage_provider.delete_file(photo.storage_path)
    GalleryRepository(db).delete_photo(photo)
    record_audit_event(
        db,
        "gallery.photo_deleted",
        context.user_id,
        "GalleryPhoto",
        photo.id,
        metadata={"domain_event": "GalleryPhotoDeleted", "gallery_id": str(gallery.id)},
    )
    db.commit()


def list_favorites(
    db: Session, gallery_id: UUID, context: AuthorizationContext
) -> list[FavoriteSelection]:
    return get_gallery(db, gallery_id, context).favorites


def add_favorite(
    db: Session,
    gallery_id: UUID,
    payload: FavoriteSelectionCreate,
    context: AuthorizationContext | None,
) -> FavoriteSelection:
    repository = GalleryRepository(db)
    gallery = (
        get_public_gallery(db, gallery_id)
        if context is None
        else get_gallery(db, gallery_id, context)
    )
    if gallery.gallery_status != GalleryStatus.SELECTION_OPEN.value:
        raise ConflictError("Favorites can only be selected while selection is open")
    photo = repository.get_photo(payload.gallery_photo_id)
    if photo is None or photo.gallery_id != gallery.id or not photo.is_active:
        raise NotFoundError("Photo not found")
    existing = repository.get_favorite_by_photo(
        gallery.id, photo.id, payload.selected_by_email
    )
    if existing is not None:
        return existing
    favorite = FavoriteSelection(
        gallery_id=gallery.id,
        gallery_photo_id=photo.id,
        selected_by_name=payload.selected_by_name,
        selected_by_email=payload.selected_by_email,
        selected_at=datetime.now(UTC),
    )
    repository.add_favorite(favorite)
    actor_id = context.user_id if context is not None else gallery.created_by_user_id
    record_audit_event(
        db,
        "gallery.favorite_selected",
        actor_id,
        "FavoriteSelection",
        favorite.id,
        metadata={"domain_event": "FavoriteSelected", "gallery_id": str(gallery.id)},
    )
    db.commit()
    db.refresh(favorite)
    return favorite


def delete_favorite(
    db: Session, gallery_id: UUID, favorite_id: UUID, context: AuthorizationContext | None
) -> None:
    repository = GalleryRepository(db)
    gallery = (
        get_public_gallery(db, gallery_id)
        if context is None
        else get_gallery(db, gallery_id, context)
    )
    favorite = repository.get_favorite(favorite_id)
    if favorite is None or favorite.gallery_id != gallery.id:
        raise NotFoundError("Favorite not found")
    repository.delete_favorite(favorite)
    db.commit()


def get_metrics(db: Session, context: AuthorizationContext) -> dict[str, int]:
    organization_id, branch_id = _scope_filters(context)
    return GalleryRepository(db).metrics(organization_id, branch_id)
