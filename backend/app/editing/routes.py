from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.editing.enums import EditingPriority, EditingStatus
from app.editing.schemas import (
    EditingAssignEditor,
    EditingDashboardRead,
    EditingJobCreate,
    EditingJobRead,
    EditingJobUpdate,
    EditingMetricsRead,
    EditingReviewCreate,
)
from app.editing.services import editing_service

router = APIRouter(prefix="/editing", tags=["Editing"])


def _job(item) -> dict:
    return EditingJobRead.model_validate(editing_service.job_to_read(item)).model_dump(mode="json")


@router.get("/jobs", response_model=APIResponse)
def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    status_filter: EditingStatus | None = Query(default=None, alias="status"),
    priority: EditingPriority | None = Query(default=None),
    assigned_editor_id: UUID | None = Query(default=None),
    branch_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:view")),
):
    result = editing_service.list_jobs(
        db,
        context,
        page=page,
        page_size=page_size,
        status=status_filter.value if status_filter else None,
        priority=priority.value if priority else None,
        assigned_editor_id=assigned_editor_id,
        branch_id=branch_id,
    )
    return api_response(
        "Editing jobs retrieved",
        [_job(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@router.post("/jobs", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_job(
    payload: EditingJobCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:create")),
):
    item = editing_service.create_job(db, payload, context)
    return api_response("Editing job created", _job(item))


@router.get("/jobs/{job_id}", response_model=APIResponse)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:view")),
):
    item = editing_service.get_job(db, job_id, context)
    return api_response("Editing job retrieved", _job(item))


@router.put("/jobs/{job_id}", response_model=APIResponse)
def update_job(
    job_id: UUID,
    payload: EditingJobUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:update")),
):
    item = editing_service.update_job(db, job_id, payload, context)
    return api_response("Editing job updated", _job(item))


@router.post("/jobs/{job_id}/assign-editor", response_model=APIResponse)
def assign_editor(
    job_id: UUID,
    payload: EditingAssignEditor,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:assign")),
):
    item = editing_service.assign_editor(db, job_id, payload, context)
    return api_response("Editor assigned", _job(item))


@router.post("/jobs/{job_id}/start", response_model=APIResponse)
def start_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:update")),
):
    item = editing_service.start_job(db, job_id, context)
    return api_response("Editing job started", _job(item))


@router.post("/jobs/{job_id}/submit-review", response_model=APIResponse)
def submit_review(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:review")),
):
    item = editing_service.submit_review(db, job_id, context)
    return api_response("Editing job submitted for review", _job(item))


@router.post("/jobs/{job_id}/approve", response_model=APIResponse)
def approve_job(
    job_id: UUID,
    payload: EditingReviewCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:approve")),
):
    item = editing_service.approve_job(db, job_id, payload, context)
    return api_response("Editing job approved", _job(item))


@router.post("/jobs/{job_id}/reject", response_model=APIResponse)
def reject_job(
    job_id: UUID,
    payload: EditingReviewCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:approve")),
):
    item = editing_service.reject_job(db, job_id, payload, context)
    return api_response("Editing job rejected", _job(item))


@router.post("/jobs/{job_id}/ready-for-delivery", response_model=APIResponse)
def mark_ready_for_delivery(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:approve")),
):
    item = editing_service.mark_ready_for_delivery(db, job_id, context)
    return api_response("Editing job ready for delivery", _job(item))


@router.get("/metrics", response_model=APIResponse)
def get_metrics(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:dashboard")),
):
    metrics = EditingMetricsRead(**editing_service.get_metrics(db, context))
    return api_response("Editing metrics retrieved", metrics.model_dump(mode="json"))


@router.get("/my-work", response_model=APIResponse)
def get_my_work(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("editing:view")),
):
    dashboard = EditingDashboardRead(**editing_service.get_my_work(db, context))
    return api_response("Editing work retrieved", dashboard.model_dump(mode="json"))
