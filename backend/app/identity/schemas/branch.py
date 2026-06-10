from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BranchBase(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=160)
    code: str = Field(min_length=1, max_length=40)
    city: str = Field(min_length=1, max_length=120)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    organization_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    code: str | None = Field(default=None, min_length=1, max_length=40)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    is_active: bool | None = None


class BranchRead(BranchBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
