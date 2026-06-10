from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.families.enums import FamilyStatus, LeadSource
from app.families.schemas import FamilyCreate, FamilyRead, FamilyUpdate
from app.families.services import family_service

router = APIRouter(prefix="/families", tags=["Families"])


def _serialize_family(item) -> dict:
    return FamilyRead.model_validate(item).model_dump(mode="json")


@router.get("", response_model=APIResponse)
def list_families(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None),
    status_filter: FamilyStatus | None = Query(default=None, alias="status"),
    source: LeadSource | None = Query(default=None),
    branch_id: UUID | None = Query(default=None),
    edd_from: date | None = Query(default=None),
    edd_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("families:read")),
):
    result = family_service.list_families(
        db,
        context,
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        status=status_filter.value if status_filter else None,
        source=source.value if source else None,
        edd_from=edd_from,
        edd_to=edd_to,
        search=search,
    )
    items = [_serialize_family(item) for item in result.items]
    return api_response("Families retrieved", items, meta=result.pagination.as_meta())


@router.get("/search", response_model=APIResponse)
def search_families(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    name: str | None = Query(default=None),
    phone: str | None = Query(default=None),
    email: str | None = Query(default=None),
    family_code: str | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("families:read")),
):
    result = family_service.search_families(
        db,
        context,
        page=page,
        page_size=page_size,
        name=name,
        phone=phone,
        email=email,
        family_code=family_code,
    )
    items = [_serialize_family(item) for item in result.items]
    return api_response("Families retrieved", items, meta=result.pagination.as_meta())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_family(
    payload: FamilyCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("families:write")),
):
    item = family_service.create_family(db, payload, context)
    return api_response("Family created", _serialize_family(item))


@router.get("/{family_id}", response_model=APIResponse)
def get_family(
    family_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("families:read")),
):
    item = family_service.get_family(db, family_id, context)
    return api_response("Family retrieved", _serialize_family(item))


@router.put("/{family_id}", response_model=APIResponse)
def update_family(
    family_id: UUID,
    payload: FamilyUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("families:write")),
):
    item = family_service.update_family(db, family_id, payload, context)
    return api_response("Family updated", _serialize_family(item))


@router.delete("/{family_id}", response_model=APIResponse)
def delete_family(
    family_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("families:delete")),
):
    family_service.delete_family(db, family_id, context)
    return api_response("Family deleted", {})
