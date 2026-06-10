from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.galleries.enums import GalleryStatus


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_required(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Value is required")
    return cleaned


class GalleryCreate(BaseModel):
    booking_id: UUID
    booking_item_id: UUID
    gallery_name: str = Field(min_length=1, max_length=160)
    gallery_status: GalleryStatus = GalleryStatus.DRAFT
    password: str | None = Field(default=None, min_length=6, max_length=128)
    expires_at: datetime | None = None

    @field_validator("gallery_name")
    @classmethod
    def clean_gallery_name(cls, value: str) -> str:
        return _clean_required(value)


class GalleryUpdate(BaseModel):
    gallery_name: str | None = Field(default=None, min_length=1, max_length=160)
    gallery_status: GalleryStatus | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
    expires_at: datetime | None = None

    @field_validator("gallery_name")
    @classmethod
    def clean_gallery_name(cls, value: str | None) -> str | None:
        return _clean_required(value) if value is not None else None


class GalleryPhotoCreate(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    storage_path: str = Field(min_length=1)
    thumbnail_path: str | None = None
    file_size: int = Field(ge=0)
    image_width: int = Field(gt=0)
    image_height: int = Field(gt=0)
    sort_order: int = 0
    is_active: bool = True

    @field_validator("file_name", "storage_path")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return _clean_required(value)

    @field_validator("thumbnail_path")
    @classmethod
    def clean_thumbnail_path(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class FavoriteSelectionCreate(BaseModel):
    gallery_photo_id: UUID
    selected_by_name: str = Field(min_length=1, max_length=160)
    selected_by_email: str | None = Field(default=None, max_length=255)

    @field_validator("selected_by_name")
    @classmethod
    def clean_selected_by_name(cls, value: str) -> str:
        return _clean_required(value)

    @field_validator("selected_by_email")
    @classmethod
    def clean_selected_by_email(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class GalleryPhotoRead(BaseModel):
    id: UUID
    gallery_id: UUID
    file_name: str
    storage_path: str
    thumbnail_path: str | None = None
    file_size: int
    image_width: int
    image_height: int
    sort_order: int
    is_active: bool
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FavoriteSelectionRead(BaseModel):
    id: UUID
    gallery_id: UUID
    gallery_photo_id: UUID
    selected_by_name: str
    selected_by_email: str | None = None
    selected_at: datetime
    gallery_photo: GalleryPhotoRead | None = None

    model_config = ConfigDict(from_attributes=True)


class GalleryBookingSummary(BaseModel):
    id: UUID
    booking_number: str
    family_id: UUID
    family_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class GalleryRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    booking_id: UUID
    booking_item_id: UUID
    gallery_name: str
    gallery_status: GalleryStatus
    created_by_user_id: UUID
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    booking_number: str | None = None
    family_name: str | None = None
    photo_count: int = 0
    favorite_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class GalleryDetailRead(GalleryRead):
    photos: list[GalleryPhotoRead] = Field(default_factory=list)
    favorites: list[FavoriteSelectionRead] = Field(default_factory=list)


class GalleryMetricsRead(BaseModel):
    total_galleries: int
    photos_uploaded: int
    selection_open_galleries: int
    selection_closed_galleries: int
    favorite_count: int
