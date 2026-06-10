from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.bookings.models import Booking, BookingItem
from app.core.database import Base
from app.identity.models import Branch, Organization, User
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Gallery(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "galleries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_gallery_branch_organization",
        ),
        UniqueConstraint("booking_item_id", name="uq_gallery_booking_item"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    booking_id: Mapped[UUID] = mapped_column(ForeignKey("bookings.id"), nullable=False, index=True)
    booking_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("booking_items.id"), nullable=False, index=True
    )
    gallery_name: Mapped[str] = mapped_column(String(160), nullable=False)
    gallery_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    selection_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    selection_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    selection_submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    selection_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    selection_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    allow_download: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_watermark: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reopen_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")
    booking: Mapped[Booking] = sa_relationship()
    booking_item: Mapped[BookingItem] = sa_relationship()
    created_by_user: Mapped[User] = sa_relationship()
    photos: Mapped[list[GalleryPhoto]] = sa_relationship(
        back_populates="gallery", cascade="all, delete-orphan"
    )
    favorites: Mapped[list[FavoriteSelection]] = sa_relationship(
        back_populates="gallery", cascade="all, delete-orphan"
    )


class GalleryPhoto(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "gallery_photos"
    __table_args__ = (
        UniqueConstraint("gallery_id", "storage_path", name="uq_gallery_photo_storage_path"),
        CheckConstraint("file_size >= 0", name="ck_gallery_photo_file_size_non_negative"),
        CheckConstraint("image_width > 0", name="ck_gallery_photo_width_positive"),
        CheckConstraint("image_height > 0", name="ck_gallery_photo_height_positive"),
    )

    gallery_id: Mapped[UUID] = mapped_column(ForeignKey("galleries.id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    image_width: Mapped[int] = mapped_column(Integer, nullable=False)
    image_height: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    gallery: Mapped[Gallery] = sa_relationship(back_populates="photos")
    favorites: Mapped[list[FavoriteSelection]] = sa_relationship(
        back_populates="gallery_photo", cascade="all, delete-orphan"
    )


class FavoriteSelection(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "favorite_selections"
    __table_args__ = (
        UniqueConstraint(
            "gallery_id",
            "gallery_photo_id",
            "selected_by_email",
            name="uq_favorite_gallery_photo_email",
        ),
    )

    gallery_id: Mapped[UUID] = mapped_column(ForeignKey("galleries.id"), nullable=False, index=True)
    gallery_photo_id: Mapped[UUID] = mapped_column(
        ForeignKey("gallery_photos.id"), nullable=False, index=True
    )
    selected_by_name: Mapped[str] = mapped_column(String(160), nullable=False)
    selected_by_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    selected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    gallery: Mapped[Gallery] = sa_relationship(back_populates="favorites")
    gallery_photo: Mapped[GalleryPhoto] = sa_relationship(back_populates="favorites")


class GalleryUpgradeRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "gallery_upgrade_requests"

    gallery_id: Mapped[UUID] = mapped_column(ForeignKey("galleries.id"), nullable=False, index=True)
    current_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    requested_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    additional_photos: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_photo: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    gallery: Mapped[Gallery] = sa_relationship()
