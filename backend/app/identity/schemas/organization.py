from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    code: str = Field(min_length=1, max_length=40)
    is_active: bool = True


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    code: str | None = Field(default=None, min_length=1, max_length=40)
    is_active: bool | None = None


class OrganizationSettingsBase(BaseModel):
    studio_name: str = Field(min_length=1, max_length=160)
    logo_url: str | None = Field(default=None, max_length=500)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=2000)
    timezone: str = Field(default="Asia/Kolkata", min_length=1, max_length=80)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    delivery_expiry_default: int = Field(default=30, ge=1, le=365)
    gallery_selection_default_limit: int = Field(default=30, ge=1, le=1000)


class OrganizationSettingsUpdate(BaseModel):
    studio_name: str | None = Field(default=None, min_length=1, max_length=160)
    logo_url: str | None = Field(default=None, max_length=500)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=2000)
    timezone: str | None = Field(default=None, min_length=1, max_length=80)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    delivery_expiry_default: int | None = Field(default=None, ge=1, le=365)
    gallery_selection_default_limit: int | None = Field(default=None, ge=1, le=1000)


class OrganizationSettingsRead(OrganizationSettingsBase):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationOnboardingDetails(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    code: str = Field(min_length=1, max_length=40)
    timezone: str = Field(default="Asia/Kolkata", min_length=1, max_length=80)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)


class OrganizationOnboardingBranch(BaseModel):
    name: str = Field(default="Main Studio", min_length=1, max_length=160)


class OrganizationOnboardingOwner(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)


class OrganizationOnboardingCreate(BaseModel):
    organization: OrganizationOnboardingDetails
    branch: OrganizationOnboardingBranch
    owner: OrganizationOnboardingOwner


class OrganizationRead(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationOnboardingRead(BaseModel):
    organization: OrganizationRead
    settings: OrganizationSettingsRead
    branch_id: UUID
    owner_id: UUID
    owner_temporary_password: str
