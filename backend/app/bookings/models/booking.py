from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.core.database import Base
from app.families.models import Family
from app.identity.models import Branch, Organization, User
from app.sales.models import Opportunity
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Package(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "packages"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_package_branch_organization",
        ),
        UniqueConstraint("branch_id", "name", name="uq_package_branch_name"),
        CheckConstraint("price >= 0", name="ck_package_price_non_negative"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    service_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")


class PackageAddon(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "package_addons"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_package_addon_branch_organization",
        ),
        UniqueConstraint("branch_id", "name", name="uq_package_addon_branch_name"),
        CheckConstraint("price >= 0", name="ck_package_addon_price_non_negative"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")


class Booking(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bookings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_booking_branch_organization",
        ),
        UniqueConstraint("booking_number", name="uq_booking_number"),
        CheckConstraint("total_amount >= 0", name="ck_booking_total_non_negative"),
        CheckConstraint("advance_received >= 0", name="ck_booking_advance_non_negative"),
        CheckConstraint("balance_amount >= 0", name="ck_booking_balance_non_negative"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    opportunity_id: Mapped[UUID] = mapped_column(
        ForeignKey("opportunities.id"), nullable=False, index=True
    )
    booking_number: Mapped[str] = mapped_column(String(40), nullable=False)
    booking_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    advance_received: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    balance_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")
    family: Mapped[Family] = sa_relationship()
    opportunity: Mapped[Opportunity] = sa_relationship()
    items: Mapped[list[BookingItem]] = sa_relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )


class BookingItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "booking_items"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_booking_item_price_non_negative"),
        CheckConstraint("discount >= 0", name="ck_booking_item_discount_non_negative"),
        CheckConstraint("final_amount >= 0", name="ck_booking_item_final_non_negative"),
    )

    booking_id: Mapped[UUID] = mapped_column(ForeignKey("bookings.id"), nullable=False, index=True)
    package_id: Mapped[UUID] = mapped_column(ForeignKey("packages.id"), nullable=False)
    service_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    final_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)

    booking: Mapped[Booking] = sa_relationship(back_populates="items")
    package: Mapped[Package] = sa_relationship()
    addons: Mapped[list[BookingItemAddon]] = sa_relationship(
        back_populates="booking_item", cascade="all, delete-orphan"
    )
    schedules: Mapped[list[ShootSchedule]] = sa_relationship(
        back_populates="booking_item", cascade="all, delete-orphan"
    )


class BookingItemAddon(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "booking_item_addons"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_booking_item_addon_price_non_negative"),
    )

    booking_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("booking_items.id"), nullable=False, index=True
    )
    addon_id: Mapped[UUID] = mapped_column(ForeignKey("package_addons.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    booking_item: Mapped[BookingItem] = sa_relationship(back_populates="addons")
    addon: Mapped[PackageAddon] = sa_relationship()


class ShootSchedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shoot_schedules"
    __table_args__ = (
        CheckConstraint("scheduled_end > scheduled_start", name="ck_schedule_end_after_start"),
    )

    booking_id: Mapped[UUID] = mapped_column(ForeignKey("bookings.id"), nullable=False, index=True)
    booking_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("booking_items.id"), nullable=False, index=True
    )
    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    shoot_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    booking: Mapped[Booking] = sa_relationship()
    booking_item: Mapped[BookingItem] = sa_relationship(back_populates="schedules")
    assignments: Mapped[list[PhotographerAssignment]] = sa_relationship(
        back_populates="shoot_schedule", cascade="all, delete-orphan"
    )


class PhotographerAssignment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "photographer_assignments"
    __table_args__ = (
        UniqueConstraint("shoot_schedule_id", "user_id", name="uq_assignment_schedule_user"),
    )

    shoot_schedule_id: Mapped[UUID] = mapped_column(
        ForeignKey("shoot_schedules.id"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    shoot_schedule: Mapped[ShootSchedule] = sa_relationship(back_populates="assignments")
    user: Mapped[User] = sa_relationship()
