from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.identity.models import Organization
from app.identity.policies import AuthorizationContext, ensure_can_access_organization
from app.identity.schemas import OrganizationCreate, OrganizationUpdate
from app.shared.exceptions.application import ConflictError, ForbiddenError, NotFoundError
from app.shared.pagination import PageResult, paginate_query
from app.shared.services.audit_service import record_audit_event


def _normalize_code(code: str) -> str:
    return code.strip().upper()


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
