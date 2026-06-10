from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PermissionRead(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
