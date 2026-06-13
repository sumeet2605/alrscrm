from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.identity.models.branch import Branch
    from app.identity.models.user import User


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    branches: Mapped[list[Branch]] = relationship(back_populates="organization")
    settings: Mapped[OrganizationSettings | None] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
        uselist=False,
    )
    users: Mapped[list[User]] = relationship(back_populates="organization", overlaps="branch,users")


class OrganizationSettings(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organization_settings"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, unique=True, index=True
    )
    studio_name: Mapped[str] = mapped_column(String(160), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(80), nullable=False, default="Asia/Kolkata")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    delivery_expiry_default: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    gallery_selection_default_limit: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30
    )

    organization: Mapped[Organization] = relationship(back_populates="settings")
