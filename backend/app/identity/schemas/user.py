from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.identity.schemas.role import RoleRead


class UserBase(BaseModel):
    organization_id: UUID
    branch_id: UUID | None = None
    username: str | None = Field(default=None, min_length=1, max_length=80)
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role_ids: list[UUID] = Field(default_factory=list)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        return _validate_password_strength(password)


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

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str | None) -> str | None:
        if password is None:
            return password
        return _validate_password_strength(password)


class UserRead(UserBase):
    id: UUID
    roles: list[RoleRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


def _validate_password_strength(password: str) -> str:
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    if not (has_upper and has_lower and has_digit):
        raise ValueError("Password must include uppercase, lowercase, and numeric characters")
    return password
