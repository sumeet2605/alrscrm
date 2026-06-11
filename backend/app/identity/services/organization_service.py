import secrets
import string
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.identity.models import Branch, Organization, OrganizationSettings, Role, User
from app.identity.policies import AuthorizationContext, ensure_can_access_organization
from app.identity.schemas import (
    OrganizationCreate,
    OrganizationOnboardingCreate,
    OrganizationSettingsUpdate,
    OrganizationUpdate,
)
from app.shared.exceptions.application import ConflictError, ForbiddenError, NotFoundError
from app.shared.pagination import PageResult, paginate_query
from app.shared.services.audit_service import record_audit_event


def _normalize_code(code: str) -> str:
    return code.strip().upper()


def _normalize_currency(currency: str) -> str:
    return currency.strip().upper()


def _default_settings(organization: Organization) -> OrganizationSettings:
    return OrganizationSettings(
        organization=organization,
        studio_name=organization.name,
        timezone="Asia/Kolkata",
        currency="INR",
        delivery_expiry_default=30,
        gallery_selection_default_limit=30,
    )


def _generate_temporary_password() -> str:
    alphabet = string.ascii_letters + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(18))
    return f"Temp{token}9a"


def _split_owner_name(name: str) -> tuple[str, str]:
    parts = name.strip().split()
    if not parts:
        return "Owner", "User"
    if len(parts) == 1:
        return parts[0], "Owner"
    return parts[0], " ".join(parts[1:])


def list_organizations(
    db: Session, context: AuthorizationContext | None = None, page: int = 1, page_size: int = 50
) -> PageResult:
    query = db.query(Organization)
    if context is not None and not context.is_platform_admin:
        query = query.filter(Organization.id == context.organization_id)
    return paginate_query(query.order_by(Organization.name), page, page_size)


def get_organization(
    db: Session, organization_id: UUID, context: AuthorizationContext | None = None
) -> Organization:
    organization = db.get(Organization, organization_id)
    if organization is None:
        raise NotFoundError("Organization not found")
    ensure_can_access_organization(context, organization)
    return organization


def create_organization(
    db: Session, payload: OrganizationCreate, context: AuthorizationContext | None = None
) -> Organization:
    if context is not None and not context.is_platform_admin:
        raise ForbiddenError("Only platform administrators can create organizations")
    data = payload.model_dump()
    data["code"] = _normalize_code(data["code"])
    organization = Organization(**data)
    organization.settings = _default_settings(organization)
    db.add(organization)
    try:
        record_audit_event(
            db,
            "organization.created",
            context.user_id if context else None,
            "Organization",
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Organization code already exists") from exc
    db.refresh(organization)
    return organization


def onboard_organization(
    db: Session, payload: OrganizationOnboardingCreate, context: AuthorizationContext
) -> tuple[Organization, OrganizationSettings, Branch, User, str]:
    if not context.is_platform_admin:
        raise ForbiddenError("Only platform administrators can onboard organizations")

    organization_code = _normalize_code(payload.organization.code)
    existing = db.query(Organization).filter(Organization.code == organization_code).one_or_none()
    if existing is not None:
        raise ConflictError("Organization code already exists")

    owner_role = db.query(Role).filter(Role.name == "Owner").one_or_none()
    if owner_role is None:
        raise NotFoundError("Owner role not found")

    organization = Organization(
        name=payload.organization.name,
        code=organization_code,
        is_active=True,
    )
    settings = OrganizationSettings(
        organization=organization,
        studio_name=payload.organization.name,
        contact_email=str(payload.organization.email) if payload.organization.email else None,
        contact_phone=payload.organization.phone,
        timezone=payload.organization.timezone,
        currency="INR",
        delivery_expiry_default=30,
        gallery_selection_default_limit=30,
    )
    branch = Branch(
        organization=organization,
        name=payload.branch.name,
        code="MAIN",
        city="Main",
        phone=payload.organization.phone,
        email=str(payload.organization.email) if payload.organization.email else None,
        is_active=True,
    )
    first_name, last_name = _split_owner_name(payload.owner.name)
    temporary_password = _generate_temporary_password()
    owner = User(
        organization=organization,
        branch=branch,
        email=str(payload.owner.email).strip().lower(),
        password_hash=hash_password(temporary_password),
        first_name=first_name,
        last_name=last_name,
        phone=payload.owner.phone,
        is_active=True,
        roles=[owner_role],
    )
    db.add_all([organization, settings, branch, owner])
    try:
        record_audit_event(
            db,
            "organization.onboarded",
            context.user_id,
            "Organization",
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Organization onboarding failed due to duplicate data") from exc
    db.refresh(organization)
    db.refresh(settings)
    db.refresh(branch)
    db.refresh(owner)
    return organization, settings, branch, owner, temporary_password


def update_organization(
    db: Session,
    organization_id: UUID,
    payload: OrganizationUpdate,
    context: AuthorizationContext | None = None,
) -> Organization:
    organization = get_organization(db, organization_id, context)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "code" and value is not None:
            value = _normalize_code(value)
        setattr(organization, field, value)
    try:
        record_audit_event(
            db,
            "organization.updated",
            context.user_id if context else None,
            "Organization",
            organization.id,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Organization code already exists") from exc
    db.refresh(organization)
    return organization


def activate_organization(
    db: Session, organization_id: UUID, context: AuthorizationContext | None = None
) -> Organization:
    organization = get_organization(db, organization_id, context)
    organization.is_active = True
    record_audit_event(
        db,
        "organization.activated",
        context.user_id if context else None,
        "Organization",
        organization.id,
    )
    db.commit()
    db.refresh(organization)
    return organization


def delete_organization(
    db: Session, organization_id: UUID, context: AuthorizationContext | None = None
) -> None:
    organization = get_organization(db, organization_id, context)
    organization.is_active = False
    record_audit_event(
        db,
        "organization.deactivated",
        context.user_id if context else None,
        "Organization",
        organization.id,
    )
    db.commit()


def get_organization_settings(
    db: Session, organization_id: UUID, context: AuthorizationContext | None = None
) -> OrganizationSettings:
    organization = get_organization(db, organization_id, context)
    settings = (
        db.query(OrganizationSettings)
        .filter(OrganizationSettings.organization_id == organization.id)
        .one_or_none()
    )
    if settings is None:
        settings = _default_settings(organization)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_organization_settings(
    db: Session,
    organization_id: UUID,
    payload: OrganizationSettingsUpdate,
    context: AuthorizationContext | None = None,
) -> OrganizationSettings:
    settings = get_organization_settings(db, organization_id, context)
    data = payload.model_dump(exclude_unset=True)
    if "currency" in data and data["currency"] is not None:
        data["currency"] = _normalize_currency(data["currency"])
    for field, value in data.items():
        setattr(settings, field, value)
    try:
        record_audit_event(
            db,
            "organization.settings_updated",
            context.user_id if context else None,
            "Organization",
            organization_id,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Organization settings update failed") from exc
    db.refresh(settings)
    return settings
