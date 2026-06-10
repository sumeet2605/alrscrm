from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.core.database import get_db
from app.identity.schemas import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.identity.services import organization_service

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("")
def list_organizations(
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:organizations:read")),
):
    items = [
        OrganizationRead.model_validate(item).model_dump(mode="json")
        for item in organization_service.list_organizations(db)
    ]
    return api_response("Organizations retrieved", items)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:organizations:write")),
):
    item = organization_service.create_organization(db, payload)
    return api_response(
        "Organization created",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.get("/{organization_id}")
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:organizations:read")),
):
    item = organization_service.get_organization(db, organization_id)
    return api_response(
        "Organization retrieved",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.patch("/{organization_id}")
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:organizations:write")),
):
    item = organization_service.update_organization(db, organization_id, payload)
    return api_response(
        "Organization updated",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.delete("/{organization_id}")
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:organizations:write")),
):
    organization_service.delete_organization(db, organization_id)
    return api_response("Organization deleted", {})
