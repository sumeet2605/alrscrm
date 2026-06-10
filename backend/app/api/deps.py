from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_token
from app.identity.models import User
from app.identity.policies import AuthorizationContext, require_permission
from app.identity.services.user_service import get_user
from app.shared.exceptions.application import ForbiddenError, NotFoundError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token, "access")
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    try:
        user = get_user(db, user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


def require_permissions(*permission_codes: str) -> Callable[[User], AuthorizationContext]:
    def dependency(current_user: User = Depends(get_current_user)) -> AuthorizationContext:
        context = AuthorizationContext.from_user(current_user)
        for permission_code in permission_codes:
            try:
                require_permission(context, permission_code)
            except ForbiddenError as exc:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                ) from exc
        return context

    return dependency


def settings_dependency():
    return get_settings()
