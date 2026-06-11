from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_json, encrypt_json
from app.identity.models import Branch
from app.identity.policies import AuthorizationContext
from app.integrations.enums import IntegrationProvider, IntegrationStatus
from app.integrations.models import OrganizationIntegration
from app.integrations.repositories import IntegrationsRepository
from app.integrations.schemas import OrganizationIntegrationCreate, OrganizationIntegrationUpdate
from app.shared.exceptions.application import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event

REQUIRED_CREDENTIALS: dict[IntegrationProvider, set[str]] = {
    IntegrationProvider.WHATSAPP_CLOUD_API: {"access_token", "phone_number_id"},
    IntegrationProvider.INSTAGRAM_BUSINESS: {"access_token", "business_account_id"},
    IntegrationProvider.FACEBOOK_PAGE: {"access_token", "page_id"},
    IntegrationProvider.SMTP_EMAIL: {"host", "port", "username", "password", "from_email"},
    IntegrationProvider.GOOGLE_CLOUD_STORAGE: {"bucket", "credentials_json"},
    IntegrationProvider.AWS_S3: {"bucket", "region", "access_key_id", "secret_access_key"},
}


def _scope_filters(
    context: AuthorizationContext, branch_id: UUID | None = None
) -> tuple[UUID | None, UUID | None]:
    if context.is_platform_admin:
        return None, branch_id
    scoped_branch_id = branch_id
    if context.is_branch_scoped:
        if branch_id is not None and branch_id != context.branch_id:
            raise ForbiddenError("Integration branch is outside the caller scope")
        scoped_branch_id = context.branch_id
    return context.organization_id, scoped_branch_id


def _ensure_branch_scope(db: Session, context: AuthorizationContext, branch_id: UUID) -> Branch:
    branch = db.get(Branch, branch_id)
    if branch is None or not branch.is_active:
        raise NotFoundError("Branch not found")
    if not context.is_platform_admin:
        if branch.organization_id != context.organization_id:
            raise ForbiddenError("Branch is outside the caller scope")
        if context.is_branch_scoped and branch.id != context.branch_id:
            raise ForbiddenError("Branch is outside the caller scope")
    return branch


def _ensure_integration_scope(
    context: AuthorizationContext, integration: OrganizationIntegration
) -> None:
    if context.is_platform_admin:
        return
    if integration.organization_id != context.organization_id:
        raise ForbiddenError("Integration is outside the caller scope")
    if context.is_branch_scoped and integration.branch_id != context.branch_id:
        raise ForbiddenError("Integration is outside the caller scope")


def _credential_keys(integration: OrganizationIntegration) -> list[str]:
    return sorted(str(key) for key in decrypt_json(integration.encrypted_credentials).keys())


def _validate_credentials(provider: IntegrationProvider, credentials: dict[str, Any]) -> None:
    required = REQUIRED_CREDENTIALS[provider]
    missing = [
        key
        for key in sorted(required)
        if credentials.get(key) is None or str(credentials.get(key)).strip() == ""
    ]
    if missing:
        raise ValidationError(f"Missing required credentials: {', '.join(missing)}")


def serialize_integration(integration: OrganizationIntegration) -> dict:
    return {
        "id": integration.id,
        "organization_id": integration.organization_id,
        "branch_id": integration.branch_id,
        "provider": integration.provider,
        "status": integration.status,
        "last_verified_at": integration.last_verified_at,
        "last_error": integration.last_error,
        "credential_keys": _credential_keys(integration),
        "created_by_user_id": integration.created_by_user_id,
        "updated_by_user_id": integration.updated_by_user_id,
        "created_at": integration.created_at,
        "updated_at": integration.updated_at,
    }


def list_integrations(
    db: Session,
    context: AuthorizationContext,
    *,
    page: int,
    page_size: int,
    branch_id: UUID | None = None,
    provider: str | None = None,
    status: str | None = None,
) -> PageResult:
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    return IntegrationsRepository(db).list(
        page=page,
        page_size=page_size,
        organization_id=organization_id,
        branch_id=scoped_branch_id,
        provider=provider,
        status=status,
    )


def get_health(db: Session, context: AuthorizationContext) -> dict[str, int]:
    organization_id, branch_id = _scope_filters(context)
    counts = IntegrationsRepository(db).health(organization_id, branch_id)
    return {
        "connected": counts.get("connected", 0),
        "disconnected": counts.get("disconnected", 0),
        "expired": counts.get("expired", 0),
        "error": counts.get("error", 0),
    }


def create_integration(
    db: Session,
    payload: OrganizationIntegrationCreate,
    context: AuthorizationContext,
) -> OrganizationIntegration:
    if not context.is_platform_admin and payload.organization_id != context.organization_id:
        raise ForbiddenError("Integration organization is outside the caller scope")
    if payload.branch_id is not None:
        branch = _ensure_branch_scope(db, context, payload.branch_id)
        if branch.organization_id != payload.organization_id:
            raise ValidationError("Integration branch must belong to organization")
    _validate_credentials(payload.provider, payload.credentials)
    repository = IntegrationsRepository(db)
    existing = repository.get_by_scope(
        payload.organization_id,
        payload.branch_id,
        payload.provider.value,
    )
    if existing is not None:
        raise ConflictError("Integration already exists for this scope and provider")
    integration = OrganizationIntegration(
        organization_id=payload.organization_id,
        branch_id=payload.branch_id,
        provider=payload.provider.value,
        encrypted_credentials=encrypt_json(payload.credentials),
        status=IntegrationStatus.DISCONNECTED.value,
        created_by_user_id=context.user_id,
        updated_by_user_id=context.user_id,
    )
    repository.add(integration)
    try:
        db.flush()
        record_audit_event(
            db,
            "integration.created",
            context.user_id,
            "OrganizationIntegration",
            integration.id,
            metadata={"provider": integration.provider},
            organization_id=integration.organization_id,
            branch_id=integration.branch_id,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Integration already exists for this scope and provider") from exc
    return get_integration(db, integration.id, context)


def get_integration(
    db: Session, integration_id: UUID, context: AuthorizationContext
) -> OrganizationIntegration:
    integration = IntegrationsRepository(db).get(integration_id)
    if integration is None:
        raise NotFoundError("Integration not found")
    _ensure_integration_scope(context, integration)
    return integration


def update_integration(
    db: Session,
    integration_id: UUID,
    payload: OrganizationIntegrationUpdate,
    context: AuthorizationContext,
) -> OrganizationIntegration:
    integration = get_integration(db, integration_id, context)
    if payload.branch_id is not None and payload.branch_id != integration.branch_id:
        branch = _ensure_branch_scope(db, context, payload.branch_id)
        if branch.organization_id != integration.organization_id:
            raise ValidationError("Integration branch must belong to organization")
        existing = IntegrationsRepository(db).get_by_scope(
            integration.organization_id,
            payload.branch_id,
            integration.provider,
        )
        if existing is not None and existing.id != integration.id:
            raise ConflictError("Integration already exists for this scope and provider")
        integration.branch_id = payload.branch_id
    if payload.credentials is not None:
        provider = IntegrationProvider(integration.provider)
        _validate_credentials(provider, payload.credentials)
        integration.encrypted_credentials = encrypt_json(payload.credentials)
        integration.status = IntegrationStatus.DISCONNECTED.value
        integration.last_error = None
    if payload.status is not None:
        integration.status = payload.status.value
    integration.updated_by_user_id = context.user_id
    record_audit_event(
        db,
        "integration.updated",
        context.user_id,
        "OrganizationIntegration",
        integration.id,
        metadata={"provider": integration.provider},
        organization_id=integration.organization_id,
        branch_id=integration.branch_id,
    )
    db.commit()
    return get_integration(db, integration.id, context)


def verify_integration(
    db: Session, integration_id: UUID, context: AuthorizationContext
) -> OrganizationIntegration:
    integration = get_integration(db, integration_id, context)
    credentials = decrypt_json(integration.encrypted_credentials)
    try:
        _validate_credentials(IntegrationProvider(integration.provider), credentials)
    except ValidationError as exc:
        integration.status = IntegrationStatus.ERROR.value
        integration.last_error = exc.message
    else:
        integration.status = IntegrationStatus.CONNECTED.value
        integration.last_error = None
        integration.last_verified_at = datetime.now(UTC)
    integration.updated_by_user_id = context.user_id
    record_audit_event(
        db,
        "integration.verified",
        context.user_id,
        "OrganizationIntegration",
        integration.id,
        metadata={"provider": integration.provider, "status": integration.status},
        organization_id=integration.organization_id,
        branch_id=integration.branch_id,
    )
    db.commit()
    return get_integration(db, integration.id, context)
