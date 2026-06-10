from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.delivery.enums import DeliveryStatus
from app.delivery.schemas import (
    ClientDeliveryRead,
    DeliveryDownloadRead,
    DeliveryJobCreate,
    DeliveryJobRead,
    DeliveryJobUpdate,
    DeliveryMetricsRead,
    DeliveryReopenRequest,
)
from app.delivery.services import delivery_service

router = APIRouter(prefix="/delivery", tags=["Delivery"])


def _job(item) -> dict:
    return DeliveryJobRead.model_validate(delivery_service.job_to_read(item)).model_dump(
        mode="json"
    )


def _client_job(item) -> dict:
    return ClientDeliveryRead.model_validate(delivery_service.client_job_to_read(item)).model_dump(
        mode="json"
    )


@router.get("/jobs", response_model=APIResponse)
def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    branch_id: UUID | None = Query(default=None),
    status_filter: DeliveryStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:view")),
):
    result = delivery_service.list_jobs(
        db,
        context,
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        status=status_filter.value if status_filter else None,
        search=search,
    )
    return api_response(
        "Delivery jobs retrieved",
        [_job(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@router.post("/jobs", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_job(
    payload: DeliveryJobCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:create")),
):
    item = delivery_service.create_job(db, payload, context)
    return api_response("Delivery job created", _job(item))


@router.get("/jobs/{job_id}", response_model=APIResponse)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:view")),
):
    item = delivery_service.get_job(db, job_id, context)
    return api_response("Delivery job retrieved", _job(item))


@router.put("/jobs/{job_id}", response_model=APIResponse)
def update_job(
    job_id: UUID,
    payload: DeliveryJobUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:update")),
):
    item = delivery_service.update_job(db, job_id, payload, context)
    return api_response("Delivery job updated", _job(item))


@router.post("/jobs/{job_id}/generate-zip", response_model=APIResponse)
def generate_zip(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:update")),
):
    item = delivery_service.generate_zip(db, job_id, context)
    return api_response("Delivery ZIP generated", _job(item))


@router.post("/jobs/{job_id}/send", response_model=APIResponse)
def send_delivery(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:send")),
):
    item = delivery_service.send_delivery(db, job_id, context)
    return api_response("Delivery sent", _job(item))


@router.post("/jobs/{job_id}/reopen-request", response_model=APIResponse)
def request_reopen(
    job_id: UUID,
    payload: DeliveryReopenRequest | None = None,
    db: Session = Depends(get_db),
):
    item = delivery_service.request_reopen(db, job_id, payload)
    return api_response("Delivery reopen requested", _client_job(item))


@router.post("/jobs/{job_id}/approve-reopen", response_model=APIResponse)
def approve_reopen(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:reopen")),
):
    item = delivery_service.approve_reopen(db, job_id, context)
    return api_response("Delivery reopened", _job(item))


@router.get("/jobs/{job_id}/downloads", response_model=APIResponse)
def list_downloads(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:download_audit")),
):
    return api_response(
        "Delivery downloads retrieved",
        [
            DeliveryDownloadRead.model_validate(item).model_dump(mode="json")
            for item in delivery_service.list_downloads(db, job_id, context)
        ],
    )


@router.get("/metrics", response_model=APIResponse)
def get_metrics(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:dashboard")),
):
    metrics = DeliveryMetricsRead(**delivery_service.get_metrics(db, context))
    return api_response("Delivery metrics retrieved", metrics.model_dump(mode="json"))


@router.get("/client/{job_id}", response_model=APIResponse)
def get_client_delivery(job_id: UUID, db: Session = Depends(get_db)):
    item = delivery_service.get_public_job(db, job_id)
    return api_response("Client delivery retrieved", _client_job(item))


@router.post("/client/{job_id}/download", response_model=APIResponse)
def download_client_delivery(
    job_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    item = delivery_service.record_download(
        db,
        job_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return api_response("Delivery downloaded", _client_job(item))
