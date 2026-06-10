from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.sales.enums import FollowUpStatus, FollowUpType, OpportunityStage, OpportunityType


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


class FamilySummaryRead(BaseModel):
    id: UUID
    family_code: str
    primary_contact_name: str
    primary_contact_phone: str
    primary_contact_email: str | None = None
    city: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserSummaryRead(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class LostReasonRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityBase(BaseModel):
    organization_id: UUID
    branch_id: UUID
    family_id: UUID
    assigned_to_user_id: UUID
    opportunity_type: OpportunityType
    current_stage: OpportunityStage = OpportunityStage.NEW
    estimated_value: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    probability: int = Field(default=0, ge=0, le=100)
    expected_booking_date: date | None = None
    lost_reason_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    branch_id: UUID | None = None
    family_id: UUID | None = None
    assigned_to_user_id: UUID | None = None
    opportunity_type: OpportunityType | None = None
    current_stage: OpportunityStage | None = None
    estimated_value: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    probability: int | None = Field(default=None, ge=0, le=100)
    expected_booking_date: date | None = None
    lost_reason_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=5000)
    stage_change_notes: str | None = Field(default=None, max_length=1000)

    @field_validator("notes", "stage_change_notes")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class FollowUpCreate(BaseModel):
    opportunity_id: UUID
    assigned_to_user_id: UUID
    followup_type: FollowUpType = FollowUpType.WHATSAPP
    due_date: date
    status: FollowUpStatus = FollowUpStatus.PENDING
    completed_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class FollowUpUpdate(BaseModel):
    assigned_to_user_id: UUID | None = None
    followup_type: FollowUpType | None = None
    due_date: date | None = None
    status: FollowUpStatus | None = None
    completed_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class FollowUpRead(BaseModel):
    id: UUID
    opportunity_id: UUID
    assigned_to_user_id: UUID
    followup_type: FollowUpType
    due_date: date
    completed_at: datetime | None = None
    status: FollowUpStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    assigned_to_user: UserSummaryRead | None = None

    model_config = ConfigDict(from_attributes=True)


class OpportunityNoteCreate(BaseModel):
    note: str = Field(min_length=1, max_length=5000)

    @field_validator("note")
    @classmethod
    def clean_note(cls, value: str) -> str:
        return _clean_required(value)


class OpportunityNoteRead(BaseModel):
    id: UUID
    opportunity_id: UUID
    created_by_user_id: UUID
    note: str
    created_at: datetime
    created_by_user: UserSummaryRead | None = None

    model_config = ConfigDict(from_attributes=True)


class OpportunityStageHistoryRead(BaseModel):
    id: UUID
    opportunity_id: UUID
    from_stage: OpportunityStage | None = None
    to_stage: OpportunityStage
    changed_by_user_id: UUID
    notes: str | None = None
    created_at: datetime
    changed_by_user: UserSummaryRead | None = None

    model_config = ConfigDict(from_attributes=True)


class OpportunityRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    family_id: UUID
    assigned_to_user_id: UUID
    opportunity_type: OpportunityType
    current_stage: OpportunityStage
    estimated_value: Decimal
    probability: int
    expected_booking_date: date | None = None
    lost_reason_id: UUID | None = None
    notes: str | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    family: FamilySummaryRead | None = None
    assigned_to_user: UserSummaryRead | None = None
    lost_reason: LostReasonRead | None = None
    followups: list[FollowUpRead] = Field(default_factory=list)
    opportunity_notes: list[OpportunityNoteRead] = Field(default_factory=list)
    stage_history: list[OpportunityStageHistoryRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PipelineRead(BaseModel):
    NEW: list[OpportunityRead] = Field(default_factory=list)
    PACKAGE_SENT: list[OpportunityRead] = Field(default_factory=list)
    INTERESTED: list[OpportunityRead] = Field(default_factory=list)
    NEED_FOLLOW_UP: list[OpportunityRead] = Field(default_factory=list)
    THINKING: list[OpportunityRead] = Field(default_factory=list)
    BOOKED: list[OpportunityRead] = Field(default_factory=list)
    LOST: list[OpportunityRead] = Field(default_factory=list)


class OpportunityMetricsRead(BaseModel):
    open_opportunities: int
    booked_opportunities: int
    lost_opportunities: int
    conversion_rate: float
    pending_followups: int
    missed_followups: int
    follow_up_compliance: float
    average_opportunity_value: float
