from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.bookings.models import Booking
from app.core.database import Base
from app.editing.models import EditingJob
from app.families.models import Family
from app.galleries.models import Gallery
from app.identity.models import Branch, Organization
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class DeliveryJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "delivery_jobs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_delivery_job_branch_organization",
        ),
        UniqueConstraint("delivery_number", name="uq_delivery_job_number"),
        UniqueConstraint("gallery_id", name="uq_delivery_job_gallery"),
        UniqueConstraint("editing_job_id", name="uq_delivery_job_editing_job"),
        CheckConstraint("edited_photo_count >= 0", name="ck_delivery_edited_count_non_negative"),
        CheckConstraint("download_count >= 0", name="ck_delivery_download_count_non_negative"),
        CheckConstraint("max_downloads >= 0", name="ck_delivery_max_downloads_non_negative"),
        CheckConstraint("re_download_fee >= 0", name="ck_delivery_re_download_fee_non_negative"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    booking_id: Mapped[UUID] = mapped_column(ForeignKey("bookings.id"), nullable=False, index=True)
    gallery_id: Mapped[UUID] = mapped_column(ForeignKey("galleries.id"), nullable=False, index=True)
    editing_job_id: Mapped[UUID] = mapped_column(
        ForeignKey("editing_jobs.id"), nullable=False, index=True
    )
    delivery_number: Mapped[str] = mapped_column(String(40), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    edited_photo_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delivery_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    delivery_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_downloads: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    allow_re_download: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    re_download_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    watermark_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    original_download_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    zip_generation_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    client_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_downloaded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivery_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")
    family: Mapped[Family] = sa_relationship()
    booking: Mapped[Booking] = sa_relationship()
    gallery: Mapped[Gallery] = sa_relationship()
    editing_job: Mapped[EditingJob] = sa_relationship()
    downloads: Mapped[list[DeliveryDownload]] = sa_relationship(
        back_populates="delivery_job", cascade="all, delete-orphan"
    )
    audits: Mapped[list[DeliveryAudit]] = sa_relationship(
        back_populates="delivery_job", cascade="all, delete-orphan"
    )


class DeliveryDownload(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "delivery_downloads"

    delivery_job_id: Mapped[UUID] = mapped_column(
        ForeignKey("delivery_jobs.id"), nullable=False, index=True
    )
    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    delivery_job: Mapped[DeliveryJob] = sa_relationship(back_populates="downloads")


class DeliveryAudit(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "delivery_audits"

    delivery_job_id: Mapped[UUID] = mapped_column(
        ForeignKey("delivery_jobs.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    event_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    delivery_job: Mapped[DeliveryJob] = sa_relationship(back_populates="audits")
