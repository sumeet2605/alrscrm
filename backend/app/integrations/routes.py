from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.integrations.enums import IntegrationProvider, IntegrationStatus
from app.integrations.schemas import (
    IntegrationHealthRead,
    OrganizationIntegrationCreate,
    OrganizationIntegrationRead,
    OrganizationIntegrationUpdate,
)
from app.integrations.services import integration_service

router = APIRouter(prefix="/integrations", tags=["Integrations"])


def _integration(item) -> dict:
    data = integration_service.serialize_integration(item)
    return OrganizationIntegrationRead.model_validate(data).model_dump(mode="json")


@router.get("", response_model=APIResponse)
def list_integrations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    branch_id: UUID | None = Query(default=None),
    provider: IntegrationProvider | None = Query(default=None),
    integration_status: IntegrationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("integrations:view")),
):
    result = integration_service.list_integrations(
        db,
        context,
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        provider=provider.value if provider else None,
        status=integration_status.value if integration_status else None,
    )
    return api_response(
        "Integrations retrieved",
        [_integration(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@router.get("/health", response_model=APIResponse)
def get_integrations_health(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("integrations:view")),
):
    data = IntegrationHealthRead(**integration_service.get_health(db, context))
    return api_response("Integration health retrieved", data.model_dump(mode="json"))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_integration(
    payload: OrganizationIntegrationCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("integrations:manage")),
):
    item = integration_service.create_integration(db, payload, context)
    return api_response("Integration created", _integration(item))


@router.patch("/{integration_id}", response_model=APIResponse)
def update_integration(
    integration_id: UUID,
    payload: OrganizationIntegrationUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("integrations:manage")),
):
    item = integration_service.update_integration(db, integration_id, payload, context)
    return api_response("Integration updated", _integration(item))


@router.post("/{integration_id}/verify", response_model=APIResponse)
def verify_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("integrations:manage")),
):
    item = integration_service.verify_integration(db, integration_id, context)
    return api_response("Integration verified", _integration(item))
