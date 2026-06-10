from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.identity.schemas import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.identity.services import organization_service

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("", response_model=APIResponse)
def list_organizations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:organizations:read")),
):
    result = organization_service.list_organizations(db, context, page, page_size)
    items = [OrganizationRead.model_validate(item).model_dump(mode="json") for item in result.items]
    return api_response("Organizations retrieved", items, meta=result.pagination.as_meta())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:organizations:write")),
):
    item = organization_service.create_organization(db, payload, context)
    return api_response(
        "Organization created",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.get("/{organization_id}", response_model=APIResponse)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:organizations:read")),
):
    item = organization_service.get_organization(db, organization_id, context)
    return api_response(
        "Organization retrieved",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.patch("/{organization_id}", response_model=APIResponse)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:organizations:write")),
):
    item = organization_service.update_organization(db, organization_id, payload, context)
    return api_response(
        "Organization updated",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.delete("/{organization_id}", response_model=APIResponse)
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:organizations:write")),
):
    organization_service.delete_organization(db, organization_id, context)
    return api_response("Organization deleted", {})
