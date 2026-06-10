from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.core.database import get_db
from app.identity.schemas import BranchCreate, BranchRead, BranchUpdate
from app.identity.services import branch_service

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("")
def list_branches(
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:branches:read")),
):
    items = [
        BranchRead.model_validate(item).model_dump(mode="json")
        for item in branch_service.list_branches(db)
    ]
    return api_response("Branches retrieved", items)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_branch(
    payload: BranchCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:branches:write")),
):
    item = branch_service.create_branch(db, payload)
    return api_response("Branch created", BranchRead.model_validate(item).model_dump(mode="json"))


@router.get("/{branch_id}")
def get_branch(
    branch_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:branches:read")),
):
    item = branch_service.get_branch(db, branch_id)
    return api_response("Branch retrieved", BranchRead.model_validate(item).model_dump(mode="json"))


@router.patch("/{branch_id}")
def update_branch(
    branch_id: UUID,
    payload: BranchUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:branches:write")),
):
    item = branch_service.update_branch(db, branch_id, payload)
    return api_response("Branch updated", BranchRead.model_validate(item).model_dump(mode="json"))


@router.delete("/{branch_id}")
def delete_branch(
    branch_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:branches:write")),
):
    branch_service.delete_branch(db, branch_id)
    return api_response("Branch deleted", {})
