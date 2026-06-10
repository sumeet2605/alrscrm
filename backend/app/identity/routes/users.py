from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.identity.schemas import UserCreate, UserRead, UserUpdate
from app.identity.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=APIResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:users:read")),
):
    result = user_service.list_users(db, context, page, page_size)
    items = [UserRead.model_validate(item).model_dump(mode="json") for item in result.items]
    return api_response("Users retrieved", items, meta=result.pagination.as_meta())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:users:write")),
):
    item = user_service.create_user(db, payload, context)
    return api_response("User created", UserRead.model_validate(item).model_dump(mode="json"))


@router.get("/{user_id}", response_model=APIResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:users:read")),
):
    item = user_service.get_user(db, user_id, context)
    return api_response("User retrieved", UserRead.model_validate(item).model_dump(mode="json"))


@router.patch("/{user_id}", response_model=APIResponse)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:users:write")),
):
    item = user_service.update_user(db, user_id, payload, context)
    return api_response("User updated", UserRead.model_validate(item).model_dump(mode="json"))


@router.delete("/{user_id}", response_model=APIResponse)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("identity:users:write")),
):
    user_service.delete_user(db, user_id, context)
    return api_response("User deleted", {})
