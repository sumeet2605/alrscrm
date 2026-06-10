from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.delivery.enums import DeliveryStatus, ZipGenerationStatus


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class DeliveryJobCreate(BaseModel):
    editing_job_id: UUID
    max_downloads: int = Field(default=10, ge=0)
    allow_re_download: bool = False
    re_download_fee: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    watermark_enabled: bool = True
    original_download_enabled: bool = False
    delivery_notes: str | None = Field(default=None, max_length=5000)

    @field_validator("delivery_notes")
    @classmethod
    def clean_delivery_notes(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class DeliveryJobUpdate(BaseModel):
    delivery_status: DeliveryStatus | None = None
    expiry_date: date | None = None
    delivery_link: str | None = Field(default=None, max_length=2000)
    max_downloads: int | None = Field(default=None, ge=0)
    allow_re_download: bool | None = None
    re_download_fee: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    watermark_enabled: bool | None = None
    original_download_enabled: bool | None = None
    zip_generation_status: ZipGenerationStatus | None = None
    delivery_notes: str | None = Field(default=None, max_length=5000)

    @field_validator("delivery_link", "delivery_notes")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class DeliveryReopenRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class DeliveryDownloadRead(BaseModel):
    id: UUID
    delivery_job_id: UUID
    downloaded_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DeliveryJobRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    family_id: UUID
    booking_id: UUID
    gallery_id: UUID
    editing_job_id: UUID
    delivery_number: str
    delivery_status: DeliveryStatus
    edited_photo_count: int
    delivery_date: date
    expiry_date: date
    delivery_link: str | None = None
    download_count: int
    max_downloads: int
    allow_re_download: bool
    re_download_fee: Decimal
    watermark_enabled: bool
    original_download_enabled: bool
    zip_generation_status: ZipGenerationStatus
    client_notified_at: datetime | None = None
    last_downloaded_at: datetime | None = None
    delivery_notes: str | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    family_name: str | None = None
    booking_number: str | None = None
    gallery_name: str | None = None
    service_type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ClientDeliveryRead(BaseModel):
    id: UUID
    delivery_number: str
    delivery_status: DeliveryStatus
    edited_photo_count: int
    delivery_date: date
    expiry_date: date
    delivery_link: str | None = None
    download_count: int
    max_downloads: int
    remaining_downloads: int
    allow_re_download: bool
    watermark_enabled: bool
    original_download_enabled: bool
    zip_generation_status: ZipGenerationStatus
    family_name: str | None = None
    booking_number: str | None = None
    gallery_name: str | None = None
    service_type: str | None = None


class DeliveryMetricsRead(BaseModel):
    pending_delivery: int
    ready_delivery: int
    delivered: int
    expired: int
    reopened: int
    average_delivery_tat: float
    downloads_this_month: int
    re_download_revenue_potential: Decimal
