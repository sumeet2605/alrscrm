from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.identity.schemas.role import RoleRead


class UserBase(BaseModel):
    organization_id: UUID
    branch_id: UUID | None = None
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role_ids: list[UUID] = Field(default_factory=list)


class UserUpdate(BaseModel):
    organization_id: UUID | None = None
    branch_id: UUID | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    first_name: str | None = Field(default=None, min_length=1, max_length=120)
    last_name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    is_active: bool | None = None
    role_ids: list[UUID] | None = None


class UserRead(UserBase):
    id: UUID
    roles: list[RoleRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
