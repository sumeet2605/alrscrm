from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.core.database import get_db
from app.identity.schemas import PermissionRead, RoleRead
from app.identity.services.rbac_service import list_permissions, list_roles

router = APIRouter(tags=["RBAC"])


@router.get("/roles")
def roles(
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:roles:read")),
):
    data = [RoleRead.model_validate(role).model_dump(mode="json") for role in list_roles(db)]
    return api_response("Roles retrieved", data)


@router.get("/permissions")
def permissions(
    db: Session = Depends(get_db),
    _=Depends(require_permissions("identity:permissions:read")),
):
    data = [
        PermissionRead.model_validate(permission).model_dump(mode="json")
        for permission in list_permissions(db)
    ]
    return api_response("Permissions retrieved", data)
