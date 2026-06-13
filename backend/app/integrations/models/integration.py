from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.core.database import Base
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.identity.models import Branch, Organization, User


class OrganizationIntegration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organization_integrations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_integration_branch_organization",
        ),
        UniqueConstraint(
            "organization_id",
            "branch_id",
            "provider",
            name="uq_integration_org_branch_provider",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    encrypted_credentials: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch | None] = sa_relationship(overlaps="organization")
    created_by_user: Mapped[User] = sa_relationship(foreign_keys=[created_by_user_id])
    updated_by_user: Mapped[User | None] = sa_relationship(foreign_keys=[updated_by_user_id])
