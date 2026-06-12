from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.identity.schemas.user import UserRead


class LoginRequest(BaseModel):
    organization_code: str = Field(min_length=1, max_length=40)
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        if not (has_upper and has_lower and has_digit):
            raise ValueError("Password must include uppercase, lowercase, and numeric characters")
        return password


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
