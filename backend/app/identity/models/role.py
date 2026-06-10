from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.identity.models.permission import Permission
    from app.identity.models.user import User


class Role(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list[User]] = relationship(secondary="user_roles", back_populates="roles")
    permissions: Mapped[list[Permission]] = relationship(
        secondary="role_permissions",
        back_populates="roles",
    )
