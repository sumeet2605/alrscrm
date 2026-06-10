from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.bookings.enums import (
    AssignmentRole,
    BookingItemStatus,
    BookingStatus,
    ServiceType,
    ShootStatus,
)
from app.sales.enums import OpportunityStage, OpportunityType


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_required(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Value is required")
    return cleaned


class FamilyBookingSummary(BaseModel):
    id: UUID
    family_code: str
    primary_contact_name: str
    primary_contact_phone: str
    primary_contact_email: str | None = None
    city: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OpportunityBookingSummary(BaseModel):
    id: UUID
    opportunity_type: OpportunityType
    current_stage: OpportunityStage
    estimated_value: Decimal

    model_config = ConfigDict(from_attributes=True)


class UserBookingSummary(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class PackageBase(BaseModel):
    organization_id: UUID
    branch_id: UUID
    name: str = Field(min_length=1, max_length=160)
    service_type: ServiceType
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return _clean_required(value)

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class PackageCreate(PackageBase):
    pass


class PackageUpdate(BaseModel):
    branch_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    service_type: ServiceType | None = None
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        return _clean_required(value) if value is not None else None

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class PackageRead(PackageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PackageAddonBase(BaseModel):
    organization_id: UUID
    branch_id: UUID
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return _clean_required(value)

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class PackageAddonCreate(PackageAddonBase):
    pass


class PackageAddonUpdate(BaseModel):
    branch_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        return _clean_required(value) if value is not None else None

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class PackageAddonRead(PackageAddonBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingItemAddonCreate(BaseModel):
    addon_id: UUID


class BookingItemAddonRead(BaseModel):
    id: UUID
    booking_item_id: UUID
    addon_id: UUID
    price: Decimal
    created_at: datetime
    addon: PackageAddonRead | None = None

    model_config = ConfigDict(from_attributes=True)


class BookingItemScheduleRead(BaseModel):
    id: UUID
    booking_id: UUID
    booking_item_id: UUID
    scheduled_start: datetime
    scheduled_end: datetime
    location: str
    shoot_status: ShootStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingItemCreate(BaseModel):
    package_id: UUID
    service_type: ServiceType
    discount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    addons: list[BookingItemAddonCreate] = Field(default_factory=list)


class BookingItemRead(BaseModel):
    id: UUID
    booking_id: UUID
    package_id: UUID
    service_type: ServiceType
    price: Decimal
    discount: Decimal
    final_amount: Decimal
    status: BookingItemStatus
    created_at: datetime
    updated_at: datetime
    package: PackageRead | None = None
    addons: list[BookingItemAddonRead] = Field(default_factory=list)
    schedules: list[BookingItemScheduleRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    organization_id: UUID
    branch_id: UUID
    family_id: UUID
    opportunity_id: UUID
    booking_status: BookingStatus = BookingStatus.PENDING_ADVANCE
    advance_received: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    booking_date: date
    notes: str | None = Field(default=None, max_length=5000)
    items: list[BookingItemCreate] = Field(min_length=1)


class BookingUpdate(BaseModel):
    booking_status: BookingStatus | None = None
    advance_received: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    booking_date: date | None = None
    notes: str | None = Field(default=None, max_length=5000)
    items: list[BookingItemCreate] | None = None


class BookingRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    family_id: UUID
    opportunity_id: UUID
    booking_number: str
    booking_status: BookingStatus
    total_amount: Decimal
    advance_received: Decimal
    balance_amount: Decimal
    booking_date: date
    notes: str | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    family: FamilyBookingSummary | None = None
    opportunity: OpportunityBookingSummary | None = None
    items: list[BookingItemRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ShootScheduleCreate(BaseModel):
    booking_id: UUID
    booking_item_id: UUID
    scheduled_start: datetime
    scheduled_end: datetime
    location: str = Field(min_length=1, max_length=255)
    shoot_status: ShootStatus = ShootStatus.SCHEDULED
    notes: str | None = Field(default=None, max_length=5000)


class ShootScheduleUpdate(BaseModel):
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    location: str | None = Field(default=None, min_length=1, max_length=255)
    shoot_status: ShootStatus | None = None
    notes: str | None = Field(default=None, max_length=5000)


class PhotographerAssignmentCreate(BaseModel):
    shoot_schedule_id: UUID
    user_id: UUID
    role: AssignmentRole


class PhotographerAssignmentRead(BaseModel):
    id: UUID
    shoot_schedule_id: UUID
    user_id: UUID
    role: AssignmentRole
    assigned_at: datetime
    user: UserBookingSummary | None = None

    model_config = ConfigDict(from_attributes=True)


class ShootScheduleRead(BaseModel):
    id: UUID
    booking_id: UUID
    booking_item_id: UUID
    scheduled_start: datetime
    scheduled_end: datetime
    location: str
    shoot_status: ShootStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    assignments: list[PhotographerAssignmentRead] = Field(default_factory=list)
    booking: BookingRead | None = None

    model_config = ConfigDict(from_attributes=True)


class BookingMetricsRead(BaseModel):
    total_bookings: int
    upcoming_shoots: int
    completed_shoots: int
    cancelled_shoots: int
    revenue_booked: float
    average_booking_value: float
    photographer_utilization: float
