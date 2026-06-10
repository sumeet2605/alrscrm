from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.identity.models.organization import Organization
    from app.identity.models.user import User


class Branch(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_branch_org_code"),
        UniqueConstraint("id", "organization_id", name="uq_branch_id_org"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    organization: Mapped[Organization] = relationship(back_populates="branches")
    users: Mapped[list[User]] = relationship(back_populates="branch", overlaps="organization,users")
