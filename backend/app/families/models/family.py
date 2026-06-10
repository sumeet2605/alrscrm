from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.core.database import Base
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.identity.models.branch import Branch
    from app.identity.models.organization import Organization


class Family(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "families"
    __table_args__ = (
        UniqueConstraint("family_code", name="uq_families_family_code"),
        UniqueConstraint("primary_contact_phone", name="uq_families_primary_contact_phone"),
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_family_branch_organization",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    family_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    primary_contact_name: Mapped[str] = mapped_column(String(160), nullable=False)
    primary_contact_phone: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    primary_contact_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    partner_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    partner_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    partner_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    expected_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")
    members: Mapped[list[FamilyMember]] = sa_relationship(
        back_populates="family", cascade="all, delete-orphan"
    )
    address: Mapped[FamilyAddress | None] = sa_relationship(
        back_populates="family", cascade="all, delete-orphan", uselist=False
    )
    service_interests: Mapped[list[ServiceInterest]] = sa_relationship(
        back_populates="family", cascade="all, delete-orphan"
    )
    tags: Mapped[list[FamilyTag]] = sa_relationship(
        secondary="family_tag_mappings", back_populates="families"
    )


class FamilyMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "family_members"

    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    relationship: Mapped[str] = mapped_column(String(40), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(40), nullable=True)

    family: Mapped[Family] = sa_relationship(back_populates="members")


class FamilyAddress(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "family_addresses"

    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id"), nullable=False, unique=True)
    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(30), nullable=False)

    family: Mapped[Family] = sa_relationship(back_populates="address")


class FamilyTag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "family_tags"

    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    families: Mapped[list[Family]] = sa_relationship(
        secondary="family_tag_mappings", back_populates="tags"
    )


class FamilyTagMapping(Base):
    __tablename__ = "family_tag_mappings"

    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id"), primary_key=True)
    tag_id: Mapped[UUID] = mapped_column(ForeignKey("family_tags.id"), primary_key=True)


class ServiceInterest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "service_interests"

    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(40), nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    family: Mapped[Family] = sa_relationship(back_populates="service_interests")
