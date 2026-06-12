from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.auth.schemas import ChangePasswordRequest, LoginRequest, RefreshRequest
from app.auth.service import (
    authenticate_user,
    change_password,
    issue_token_pair,
    refresh_access_token,
    revoke_refresh_token,
)
from app.core.database import get_db
from app.identity.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=APIResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    user = authenticate_user(
        db,
        payload.organization_code,
        payload.email,
        payload.password,
        ip_address,
    )
    tokens = issue_token_pair(
        db,
        user.id,
        ip_address,
        request.headers.get("user-agent"),
    )
    data = {**tokens, "user": UserRead.model_validate(user).model_dump(mode="json")}
    return api_response("Login successful", data)


@router.post("/refresh", response_model=APIResponse)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    return api_response(
        "Token refreshed",
        refresh_access_token(
            db,
            payload.refresh_token,
            request.client.host if request.client else None,
            request.headers.get("user-agent"),
        ),
    )


@router.post("/logout", response_model=APIResponse)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    revoke_refresh_token(db, payload.refresh_token)
    return api_response("Logged out", {})


@router.post("/change-password", response_model=APIResponse)
def update_own_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tokens = change_password(
        db,
        current_user,
        payload.current_password,
        payload.new_password,
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    refreshed_user = UserRead.model_validate(current_user).model_dump(mode="json")
    refreshed_user["password_reset_required"] = False
    return api_response("Password changed", {**tokens, "user": refreshed_user})


@router.get("/me", response_model=APIResponse)
def me(current_user=Depends(get_current_user)):
    return api_response(
        "Authenticated user",
        UserRead.model_validate(current_user).model_dump(mode="json"),
    )
