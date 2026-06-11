from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.integrations.enums import IntegrationProvider, IntegrationStatus


class OrganizationIntegrationCreate(BaseModel):
    organization_id: UUID
    branch_id: UUID | None = None
    provider: IntegrationProvider
    credentials: dict[str, Any] = Field(min_length=1)

    @field_validator("credentials")
    @classmethod
    def validate_credentials(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("Credentials are required")
        return value


class OrganizationIntegrationUpdate(BaseModel):
    branch_id: UUID | None = None
    credentials: dict[str, Any] | None = Field(default=None, min_length=1)
    status: IntegrationStatus | None = None


class OrganizationIntegrationRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID | None = None
    provider: IntegrationProvider
    status: IntegrationStatus
    last_verified_at: datetime | None = None
    last_error: str | None = None
    credential_keys: list[str]
    created_by_user_id: UUID
    updated_by_user_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntegrationHealthRead(BaseModel):
    connected: int
    disconnected: int
    expired: int
    error: int
