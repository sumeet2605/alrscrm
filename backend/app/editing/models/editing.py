from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
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
from app.galleries.models import Gallery
from app.identity.models import Branch, Organization, User
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class EditingJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "editing_jobs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_editing_job_branch_organization",
        ),
        UniqueConstraint("gallery_id", name="uq_editing_job_gallery"),
        CheckConstraint(
            "selected_photo_count >= 0",
            name="ck_editing_selected_photo_count_non_negative",
        ),
        CheckConstraint(
            "completed_photo_count >= 0",
            name="ck_editing_completed_photo_count_non_negative",
        ),
        CheckConstraint(
            "completed_photo_count <= selected_photo_count",
            name="ck_editing_completed_not_over_selected",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    booking_id: Mapped[UUID] = mapped_column(ForeignKey("bookings.id"), nullable=False, index=True)
    booking_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("booking_items.id"), nullable=False, index=True
    )
    gallery_id: Mapped[UUID] = mapped_column(ForeignKey("galleries.id"), nullable=False, index=True)
    assigned_editor_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    priority: Mapped[str] = mapped_column(String(40), nullable=False)
    editing_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    selected_photo_count: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_photo_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")
    booking: Mapped[Booking] = sa_relationship()
    booking_item: Mapped[BookingItem] = sa_relationship()
    gallery: Mapped[Gallery] = sa_relationship()
    assigned_editor: Mapped[User | None] = sa_relationship()
    reviews: Mapped[list[EditingReview]] = sa_relationship(
        back_populates="editing_job", cascade="all, delete-orphan"
    )


class EditingReview(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "editing_reviews"

    editing_job_id: Mapped[UUID] = mapped_column(
        ForeignKey("editing_jobs.id"), nullable=False, index=True
    )
    reviewed_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    review_status: Mapped[str] = mapped_column(String(40), nullable=False)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    editing_job: Mapped[EditingJob] = sa_relationship(back_populates="reviews")
    reviewed_by_user: Mapped[User] = sa_relationship()
