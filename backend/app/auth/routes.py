from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.responses import api_response
from app.auth.schemas import LoginRequest, RefreshRequest
from app.auth.service import authenticate_user, issue_token_pair, refresh_access_token
from app.core.database import get_db
from app.identity.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    tokens = issue_token_pair(user.id)
    data = {**tokens, "user": UserRead.model_validate(user).model_dump(mode="json")}
    return api_response("Login successful", data)


@router.post("/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return api_response("Token refreshed", refresh_access_token(db, payload.refresh_token))


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return api_response(
        "Authenticated user",
        UserRead.model_validate(current_user).model_dump(mode="json"),
    )
