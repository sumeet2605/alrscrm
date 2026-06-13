from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.identity.schemas import (
    OrganizationCreate,
    OrganizationOnboardingCreate,
    OrganizationOnboardingRead,
    OrganizationRead,
    OrganizationSettingsRead,
    OrganizationSettingsUpdate,
    OrganizationUpdate,
)
from app.identity.services import organization_service

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("", response_model=APIResponse)
def list_organizations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:view")),
):
    result = organization_service.list_organizations(db, context, page, page_size)
    items = [OrganizationRead.model_validate(item).model_dump(mode="json") for item in result.items]
    return api_response("Organizations retrieved", items, meta=result.pagination.as_meta())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:create")),
):
    item = organization_service.create_organization(db, payload, context)
    return api_response(
        "Organization created",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/onboard", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def onboard_organization(
    payload: OrganizationOnboardingCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:onboard")),
):
    organization, settings, branch, owner, temporary_password = (
        organization_service.onboard_organization(db, payload, context)
    )
    data = OrganizationOnboardingRead(
        organization=OrganizationRead.model_validate(organization),
        settings=OrganizationSettingsRead.model_validate(settings),
        branch_id=branch.id,
        owner_id=owner.id,
        owner_temporary_password=temporary_password,
    ).model_dump(mode="json")
    return api_response("Organization onboarded", data)


@router.get("/{organization_id}", response_model=APIResponse)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:view")),
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
    context=Depends(require_permissions("organizations:update")),
):
    item = organization_service.update_organization(db, organization_id, payload, context)
    return api_response(
        "Organization updated",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/{organization_id}/activate", response_model=APIResponse)
def activate_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:update")),
):
    item = organization_service.activate_organization(db, organization_id, context)
    return api_response(
        "Organization activated",
        OrganizationRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/{organization_id}/deactivate", response_model=APIResponse)
def deactivate_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:deactivate")),
):
    organization_service.delete_organization(db, organization_id, context)
    return api_response("Organization deactivated", {})


@router.get("/{organization_id}/settings", response_model=APIResponse)
def get_organization_settings(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:view")),
):
    item = organization_service.get_organization_settings(db, organization_id, context)
    return api_response(
        "Organization settings retrieved",
        OrganizationSettingsRead.model_validate(item).model_dump(mode="json"),
    )


@router.patch("/{organization_id}/settings", response_model=APIResponse)
def update_organization_settings(
    organization_id: UUID,
    payload: OrganizationSettingsUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:update")),
):
    item = organization_service.update_organization_settings(db, organization_id, payload, context)
    return api_response(
        "Organization settings updated",
        OrganizationSettingsRead.model_validate(item).model_dump(mode="json"),
    )


@router.delete("/{organization_id}", response_model=APIResponse)
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("organizations:deactivate")),
):
    organization_service.delete_organization(db, organization_id, context)
    return api_response("Organization deleted", {})
