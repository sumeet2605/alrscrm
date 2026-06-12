from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.delivery.enums import DeliveryStatus
from app.delivery.schemas import (
    ClientDeliveryRead,
    DeliveryAuthenticateRequest,
    DeliveryAuthenticateResponse,
    DeliveryDownloadRead,
    DeliveryDownloadResponse,
    DeliveryJobCreate,
    DeliveryJobRead,
    DeliveryJobUpdate,
    DeliveryMetricsRead,
    DeliveryReopenRequest,
)
from app.delivery.services import delivery_service
from app.galleries.storage import StorageProvider, get_storage_provider
from app.shared.exceptions.application import UnauthorizedError

router = APIRouter(prefix="/delivery", tags=["Delivery"])


def _job(item) -> dict:
    return DeliveryJobRead.model_validate(delivery_service.job_to_read(item)).model_dump(
        mode="json"
    )


def _client_job(item) -> dict:
    return ClientDeliveryRead.model_validate(delivery_service.client_job_to_read(item)).model_dump(
        mode="json"
    )


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise UnauthorizedError("Delivery session required")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Delivery session required")
    return parts[1]


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
    storage_provider: StorageProvider = Depends(get_storage_provider),
):
    item = delivery_service.generate_zip(db, job_id, context, storage_provider)
    return api_response("Delivery ZIP generated", _job(item))


@router.post("/jobs/{job_id}/send", response_model=APIResponse)
def send_delivery(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:send")),
):
    item = delivery_service.send_delivery(db, job_id, context)
    return api_response("Delivery sent", _job(item))


@router.post("/jobs/{job_id}/approve-reopen", response_model=APIResponse)
def approve_reopen(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:reopen")),
):
    item = delivery_service.approve_reopen(db, job_id, context)
    return api_response("Delivery reopened", _job(item))


@router.post("/jobs/{job_id}/close", response_model=APIResponse)
def close_delivery(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:update")),
):
    item = delivery_service.close_job(db, job_id, context)
    return api_response("Delivery closed", _job(item))


@router.post("/jobs/{job_id}/access-token/rotate", response_model=APIResponse)
def rotate_access_token(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:send")),
):
    item = delivery_service.rotate_job_access_token(db, job_id, context)
    return api_response("Delivery access token rotated", _job(item))


@router.post("/jobs/{job_id}/access-token/revoke", response_model=APIResponse)
def revoke_access_token(
    job_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("delivery:send")),
):
    item = delivery_service.revoke_access_tokens(db, job_id, context)
    return api_response("Delivery access tokens revoked", _job(item))


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


@router.post("/public/authenticate", response_model=APIResponse)
def authenticate_public_delivery(
    payload: DeliveryAuthenticateRequest,
    db: Session = Depends(get_db),
):
    session = DeliveryAuthenticateResponse(
        **delivery_service.authenticate_public_delivery(db, payload)
    )
    return api_response("Delivery authenticated", session.model_dump(mode="json"))


@router.get("/client/{token}", response_model=APIResponse)
def get_client_delivery(token: str, db: Session = Depends(get_db)):
    item = delivery_service.get_public_job_by_token(db, token)
    return api_response("Client delivery retrieved", _client_job(item))


@router.post("/client/{token}/download", response_model=APIResponse)
def download_client_delivery(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
    storage_provider: StorageProvider = Depends(get_storage_provider),
    authorization: str | None = Header(default=None),
):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    item = delivery_service.record_download(
        db,
        token,
        _bearer_token(authorization),
        storage_provider,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return api_response(
        "Delivery download URL generated",
        DeliveryDownloadResponse(**item).model_dump(mode="json"),
    )


@router.post("/client/{token}/reopen-request", response_model=APIResponse)
def request_reopen(
    token: str,
    payload: DeliveryReopenRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    item = delivery_service.request_reopen(db, token, payload, ip_address=ip_address)
    return api_response("Delivery reopen requested", _client_job(item))
