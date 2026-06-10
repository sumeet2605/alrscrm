from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.editing.enums import EditingPriority, EditingReviewStatus, EditingStatus


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class EditingJobCreate(BaseModel):
    gallery_id: UUID
    priority: EditingPriority = EditingPriority.NORMAL
    due_date: date | None = None
    assigned_editor_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class EditingJobUpdate(BaseModel):
    priority: EditingPriority | None = None
    editing_status: EditingStatus | None = None
    completed_photo_count: int | None = Field(default=None, ge=0)
    due_date: date | None = None
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class EditingAssignEditor(BaseModel):
    assigned_editor_id: UUID
    due_date: date | None = None


class EditingReviewCreate(BaseModel):
    review_notes: str | None = Field(default=None, max_length=5000)

    @field_validator("review_notes")
    @classmethod
    def clean_review_notes(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class EditingUserSummary(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class EditingReviewRead(BaseModel):
    id: UUID
    editing_job_id: UUID
    reviewed_by_user_id: UUID
    review_status: EditingReviewStatus
    review_notes: str | None = None
    reviewed_at: datetime
    reviewed_by_user: EditingUserSummary | None = None

    model_config = ConfigDict(from_attributes=True)


class EditingJobRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    booking_id: UUID
    booking_item_id: UUID
    gallery_id: UUID
    assigned_editor_id: UUID | None = None
    priority: EditingPriority
    editing_status: EditingStatus
    selected_photo_count: int
    completed_photo_count: int
    due_date: date
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    assigned_editor: EditingUserSummary | None = None
    reviews: list[EditingReviewRead] = Field(default_factory=list)
    gallery_name: str | None = None
    booking_number: str | None = None
    family_name: str | None = None
    service_type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EditingMetricsRead(BaseModel):
    pending_jobs: int
    assigned_jobs: int
    in_progress_jobs: int
    ready_for_review: int
    ready_for_delivery: int
    overdue_jobs: int
    average_editing_tat: float
    average_review_tat: float
    jobs_by_editor: dict[str, int]
    jobs_by_priority: dict[str, int]
    jobs_by_service_type: dict[str, int]
    photos_edited_this_month: int


class EditingDashboardRead(BaseModel):
    assigned_jobs: int
    due_today: int
    overdue: int
    completed_this_week: int
    current_workload: int
