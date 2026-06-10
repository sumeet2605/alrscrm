from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.identity.schemas.permission import PermissionRead


class RoleRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    permissions: list[PermissionRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
