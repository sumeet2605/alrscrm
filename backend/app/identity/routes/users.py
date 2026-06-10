from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.core.database import get_db
from app.identity.schemas import UserCreate, UserRead, UserUpdate
from app.identity.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
def list_users(
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:users:read")),
):
    items = [
        UserRead.model_validate(item).model_dump(mode="json")
        for item in user_service.list_users(db)
    ]
    return api_response("Users retrieved", items)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:users:write")),
):
    item = user_service.create_user(db, payload)
    return api_response("User created", UserRead.model_validate(item).model_dump(mode="json"))


@router.get("/{user_id}")
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:users:read")),
):
    item = user_service.get_user(db, user_id)
    return api_response("User retrieved", UserRead.model_validate(item).model_dump(mode="json"))


@router.patch("/{user_id}")
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:users:write")),
):
    item = user_service.update_user(db, user_id, payload)
    return api_response("User updated", UserRead.model_validate(item).model_dump(mode="json"))


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:users:write")),
):
    user_service.delete_user(db, user_id)
    return api_response("User deleted", {})
