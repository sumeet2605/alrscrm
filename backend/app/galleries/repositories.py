from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.bookings.models import Booking, BookingItem
from app.families.models import Family
from app.galleries.enums import GalleryStatus
from app.galleries.models import FavoriteSelection, Gallery, GalleryPhoto
from app.galleries.schemas.gallery import GalleryUpdate
from app.shared.pagination import PageResult, paginate_query


class GalleryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def gallery_options(self):
        return (
            joinedload(Gallery.booking).joinedload(Booking.family),
            joinedload(Gallery.booking_item).joinedload(BookingItem.package),
            selectinload(Gallery.photos),
            selectinload(Gallery.favorites).joinedload(FavoriteSelection.gallery_photo),
        )

    def list_galleries(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        gallery_status: str | None = None,
        search: str | None = None,
    ) -> PageResult:
        query = self.db.query(Gallery).options(*self.gallery_options())
        if organization_id is not None:
            query = query.filter(Gallery.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Gallery.branch_id == branch_id)
        if gallery_status is not None:
            query = query.filter(Gallery.gallery_status == gallery_status)
        if search:
            needle = f"%{search.strip().lower()}%"
            query = query.join(Booking, Gallery.booking_id == Booking.id).join(
                Family, Booking.family_id == Family.id
            ).filter(
                func.lower(Gallery.gallery_name).like(needle)
                | func.lower(Booking.booking_number).like(needle)
                | func.lower(Family.primary_contact_name).like(needle)
            )
        return paginate_query(query.order_by(Gallery.created_at.desc()), page, page_size)

    def get_gallery(self, gallery_id: UUID) -> Gallery | None:
        return (
            self.db.query(Gallery)
            .options(*self.gallery_options())
            .filter(Gallery.id == gallery_id)
            .one_or_none()
        )

    def create_gallery(self, gallery: Gallery) -> Gallery:
        self.db.add(gallery)
        return gallery

    def update_gallery(self, gallery: Gallery, payload: GalleryUpdate, password_hash: str | None):
        for field, value in payload.model_dump(
            exclude_unset=True, exclude={"password"}
        ).items():
            setattr(gallery, field, value)
        if payload.password is not None:
            gallery.password_hash = password_hash

    def add_photo(self, photo: GalleryPhoto) -> GalleryPhoto:
        self.db.add(photo)
        return photo

    def get_photo(self, photo_id: UUID) -> GalleryPhoto | None:
        return self.db.get(GalleryPhoto, photo_id)

    def delete_photo(self, photo: GalleryPhoto) -> None:
        photo.is_active = False

    def add_favorite(self, favorite: FavoriteSelection) -> FavoriteSelection:
        self.db.add(favorite)
        return favorite

    def get_favorite(self, favorite_id: UUID) -> FavoriteSelection | None:
        return self.db.get(FavoriteSelection, favorite_id)

    def get_favorite_by_photo(
        self, gallery_id: UUID, photo_id: UUID, selected_by_email: str | None
    ) -> FavoriteSelection | None:
        query = self.db.query(FavoriteSelection).filter(
            FavoriteSelection.gallery_id == gallery_id,
            FavoriteSelection.gallery_photo_id == photo_id,
        )
        if selected_by_email is None:
            query = query.filter(FavoriteSelection.selected_by_email.is_(None))
        else:
            query = query.filter(FavoriteSelection.selected_by_email == selected_by_email)
        return query.one_or_none()

    def delete_favorite(self, favorite: FavoriteSelection) -> None:
        self.db.delete(favorite)

    def booking_item_for_gallery(
        self, booking_id: UUID, booking_item_id: UUID
    ) -> BookingItem | None:
        return (
            self.db.query(BookingItem)
            .options(joinedload(BookingItem.booking), joinedload(BookingItem.package))
            .filter(BookingItem.id == booking_item_id, BookingItem.booking_id == booking_id)
            .one_or_none()
        )

    def metrics(self, organization_id: UUID | None, branch_id: UUID | None) -> dict[str, int]:
        gallery_query = self.db.query(Gallery)
        photo_query = self.db.query(GalleryPhoto).join(Gallery)
        favorite_query = self.db.query(FavoriteSelection).join(Gallery)
        if organization_id is not None:
            gallery_query = gallery_query.filter(Gallery.organization_id == organization_id)
            photo_query = photo_query.filter(Gallery.organization_id == organization_id)
            favorite_query = favorite_query.filter(Gallery.organization_id == organization_id)
        if branch_id is not None:
            gallery_query = gallery_query.filter(Gallery.branch_id == branch_id)
            photo_query = photo_query.filter(Gallery.branch_id == branch_id)
            favorite_query = favorite_query.filter(Gallery.branch_id == branch_id)
        return {
            "total_galleries": gallery_query.count(),
            "photos_uploaded": photo_query.filter(GalleryPhoto.is_active.is_(True)).count(),
            "selection_open_galleries": gallery_query.filter(
                Gallery.gallery_status == GalleryStatus.SELECTION_OPEN.value
            ).count(),
            "selection_closed_galleries": gallery_query.filter(
                Gallery.gallery_status == GalleryStatus.SELECTION_CLOSED.value
            ).count(),
            "favorite_count": favorite_query.count(),
        }

    def next_photo_sort_order(self, gallery_id: UUID) -> int:
        current = (
            self.db.query(func.max(GalleryPhoto.sort_order))
            .filter(GalleryPhoto.gallery_id == gallery_id)
            .scalar()
        )
        return int(current or 0) + 1

    def make_photo(self, gallery_id: UUID, **kwargs) -> GalleryPhoto:
        return GalleryPhoto(gallery_id=gallery_id, uploaded_at=datetime.now(UTC), **kwargs)
