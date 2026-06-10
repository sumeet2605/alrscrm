from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.identity.schemas import BranchCreate, BranchRead, BranchUpdate
from app.identity.services import branch_service

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("", response_model=APIResponse)
def list_branches(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:branches:read")),
):
    result = branch_service.list_branches(db, context, page, page_size)
    items = [BranchRead.model_validate(item).model_dump(mode="json") for item in result.items]
    return api_response("Branches retrieved", items, meta=result.pagination.as_meta())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_branch(
    payload: BranchCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:branches:write")),
):
    item = branch_service.create_branch(db, payload, context)
    return api_response("Branch created", BranchRead.model_validate(item).model_dump(mode="json"))


@router.get("/{branch_id}", response_model=APIResponse)
def get_branch(
    branch_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:branches:read")),
):
    item = branch_service.get_branch(db, branch_id, context)
    return api_response("Branch retrieved", BranchRead.model_validate(item).model_dump(mode="json"))


@router.patch("/{branch_id}", response_model=APIResponse)
def update_branch(
    branch_id: UUID,
    payload: BranchUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:branches:write")),
):
    item = branch_service.update_branch(db, branch_id, payload, context)
    return api_response("Branch updated", BranchRead.model_validate(item).model_dump(mode="json"))


@router.delete("/{branch_id}", response_model=APIResponse)
def delete_branch(
    branch_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:branches:write")),
):
    branch_service.delete_branch(db, branch_id, context)
    return api_response("Branch deleted", {})
