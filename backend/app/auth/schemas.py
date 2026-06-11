from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.identity.schemas.user import UserRead


class LoginRequest(BaseModel):
    organization_code: str = Field(min_length=1, max_length=40)
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthenticatedUser(BaseModel):
    user_id: UUID
    email: EmailStr
    roles: list[str]


class LoginResponse(TokenPair):
    user: UserRead
