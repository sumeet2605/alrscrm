from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.identity.models.role import Role


class Permission(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        secondary="role_permissions",
        back_populates="permissions",
    )
