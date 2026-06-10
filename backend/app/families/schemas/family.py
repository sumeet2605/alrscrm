from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.families.enums import FamilyStatus, Gender, LeadSource, Relationship, ServiceType


def _clean_optional_string(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_required_string(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Value is required")
    return cleaned


class FamilyMemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    relationship: Relationship
    date_of_birth: date | None = None
    gender: Gender | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return _clean_required_string(value)


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    relationship: Relationship | None = None
    date_of_birth: date | None = None
    gender: Gender | None = None


class FamilyMemberRead(FamilyMemberBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FamilyAddressBase(BaseModel):
    address_line_1: str = Field(min_length=1, max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=120)
    state: str = Field(min_length=1, max_length=120)
    country: str = Field(min_length=1, max_length=120)
    postal_code: str = Field(min_length=1, max_length=30)

    @field_validator("address_line_1", "city", "state", "country", "postal_code")
    @classmethod
    def clean_required_strings(cls, value: str) -> str:
        return _clean_required_string(value)

    @field_validator("address_line_2")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class FamilyAddressCreate(FamilyAddressBase):
    pass


class FamilyAddressUpdate(BaseModel):
    address_line_1: str | None = Field(default=None, min_length=1, max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    state: str | None = Field(default=None, min_length=1, max_length=120)
    country: str | None = Field(default=None, min_length=1, max_length=120)
    postal_code: str | None = Field(default=None, min_length=1, max_length=30)


class FamilyAddressRead(FamilyAddressBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceInterestBase(BaseModel):
    service_type: ServiceType
    priority: int = Field(default=1, ge=1, le=5)
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class ServiceInterestCreate(ServiceInterestBase):
    pass


class ServiceInterestUpdate(BaseModel):
    service_type: ServiceType | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = Field(default=None, max_length=1000)


class ServiceInterestRead(ServiceInterestBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FamilyBase(BaseModel):
    organization_id: UUID
    branch_id: UUID
    primary_contact_name: str = Field(min_length=1, max_length=160)
    primary_contact_phone: str = Field(min_length=6, max_length=30)
    primary_contact_email: EmailStr | None = None
    partner_name: str | None = Field(default=None, max_length=160)
    partner_phone: str | None = Field(default=None, max_length=30)
    partner_email: EmailStr | None = None
    city: str | None = Field(default=None, max_length=120)
    expected_delivery_date: date | None = None
    source: LeadSource = LeadSource.OTHER
    notes: str | None = Field(default=None, max_length=5000)
    status: FamilyStatus = FamilyStatus.INQUIRY
    members: list[FamilyMemberCreate] = Field(default_factory=list)
    address: FamilyAddressCreate | None = None
    service_interests: list[ServiceInterestCreate] = Field(default_factory=list)

    @field_validator("primary_contact_name", "primary_contact_phone")
    @classmethod
    def clean_required_strings(cls, value: str) -> str:
        return _clean_required_string(value)

    @field_validator("partner_name", "partner_phone", "city", "notes")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional_string(value)


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(BaseModel):
    branch_id: UUID | None = None
    primary_contact_name: str | None = Field(default=None, min_length=1, max_length=160)
    primary_contact_phone: str | None = Field(default=None, min_length=6, max_length=30)
    primary_contact_email: EmailStr | None = None
    partner_name: str | None = Field(default=None, max_length=160)
    partner_phone: str | None = Field(default=None, max_length=30)
    partner_email: EmailStr | None = None
    city: str | None = Field(default=None, max_length=120)
    expected_delivery_date: date | None = None
    source: LeadSource | None = None
    notes: str | None = Field(default=None, max_length=5000)
    status: FamilyStatus | None = None
    members: list[FamilyMemberCreate] | None = None
    address: FamilyAddressCreate | None = None
    service_interests: list[ServiceInterestCreate] | None = None


class FamilyRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    family_code: str
    primary_contact_name: str
    primary_contact_phone: str
    primary_contact_email: EmailStr | None
    partner_name: str | None
    partner_phone: str | None
    partner_email: EmailStr | None
    city: str | None
    expected_delivery_date: date | None
    source: LeadSource
    notes: str | None
    status: FamilyStatus
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    members: list[FamilyMemberRead] = Field(default_factory=list)
    address: FamilyAddressRead | None = None
    service_interests: list[ServiceInterestRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
