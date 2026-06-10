from datetime import date
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.families.models import Family
from app.families.repositories import FamilyRepository
from app.families.schemas import FamilyCreate, FamilyUpdate
from app.identity.models import Branch, Organization
from app.identity.policies import AuthorizationContext
from app.shared.exceptions.application import ConflictError, ForbiddenError, NotFoundError
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event


def _scope_filters(
    context: AuthorizationContext,
    organization_id: UUID | None = None,
    branch_id: UUID | None = None,
) -> tuple[UUID | None, UUID | None]:
    if context.is_platform_admin:
        return organization_id, branch_id
    scoped_org_id = context.organization_id
    scoped_branch_id = branch_id
    if context.is_branch_scoped:
        if branch_id is not None and branch_id != context.branch_id:
            raise ForbiddenError("Family branch is outside the caller scope")
        scoped_branch_id = context.branch_id
    return scoped_org_id, scoped_branch_id


def _ensure_branch_scope(db: Session, context: AuthorizationContext, branch_id: UUID) -> Branch:
    branch = db.get(Branch, branch_id)
    if branch is None or not branch.is_active:
        raise NotFoundError("Branch not found")
    if not context.is_platform_admin:
        if branch.organization_id != context.organization_id:
            raise ForbiddenError("Family branch is outside the caller scope")
        if context.is_branch_scoped and branch.id != context.branch_id:
            raise ForbiddenError("Family branch is outside the caller scope")
    return branch


def _ensure_organization(db: Session, organization_id: UUID) -> None:
    organization = db.get(Organization, organization_id)
    if organization is None or not organization.is_active:
        raise NotFoundError("Organization not found")


def _ensure_family_scope(context: AuthorizationContext, family: Family) -> None:
    if context.is_platform_admin:
        return
    if family.organization_id != context.organization_id:
        raise ForbiddenError("Family is outside the caller scope")
    if context.is_branch_scoped and family.branch_id != context.branch_id:
        raise ForbiddenError("Family is outside the caller scope")


def list_families(
    db: Session,
    context: AuthorizationContext,
    *,
    page: int = 1,
    page_size: int = 50,
    organization_id: UUID | None = None,
    branch_id: UUID | None = None,
    status: str | None = None,
    source: str | None = None,
    edd_from: date | None = None,
    edd_to: date | None = None,
    search: str | None = None,
) -> PageResult:
    scoped_org_id, scoped_branch_id = _scope_filters(context, organization_id, branch_id)
    return FamilyRepository(db).list(
        page=page,
        page_size=page_size,
        organization_id=scoped_org_id,
        branch_id=scoped_branch_id,
        status=status,
        source=source,
        edd_from=edd_from,
        edd_to=edd_to,
        search=search,
    )


def search_families(
    db: Session,
    context: AuthorizationContext,
    *,
    page: int = 1,
    page_size: int = 50,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    family_code: str | None = None,
) -> PageResult:
    search = next((value for value in (name, phone, email, family_code) if value), None)
    return list_families(db, context, page=page, page_size=page_size, search=search)


def get_family(db: Session, family_id: UUID, context: AuthorizationContext) -> Family:
    family = FamilyRepository(db).get(family_id)
    if family is None:
        raise NotFoundError("Family not found")
    _ensure_family_scope(context, family)
    return family


def create_family(db: Session, payload: FamilyCreate, context: AuthorizationContext) -> Family:
    _ensure_organization(db, payload.organization_id)
    if not context.is_platform_admin and payload.organization_id != context.organization_id:
        raise ForbiddenError("Family organization is outside the caller scope")
    _ensure_branch_scope(db, context, payload.branch_id)

    repository = FamilyRepository(db)
    if repository.exists_by_phone(payload.primary_contact_phone):
        raise ConflictError("Family already exists for primary phone")
    family = repository.create(payload, repository.next_family_code())
    try:
        record_audit_event(db, "family.created", context.user_id, "Family")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Family phone or code already exists") from exc
    db.refresh(family)
    return get_family(db, family.id, context)


def update_family(
    db: Session,
    family_id: UUID,
    payload: FamilyUpdate,
    context: AuthorizationContext,
) -> Family:
    repository = FamilyRepository(db)
    family = get_family(db, family_id, context)
    if payload.branch_id is not None:
        branch = _ensure_branch_scope(db, context, payload.branch_id)
        family.organization_id = branch.organization_id
    if payload.primary_contact_phone is not None and repository.exists_by_phone(
        payload.primary_contact_phone, family.id
    ):
        raise ConflictError("Family already exists for primary phone")
    repository.update_scalar_fields(family, payload)
    repository.replace_nested(family, payload)
    try:
        record_audit_event(db, "family.updated", context.user_id, "Family", family.id)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Family phone or code already exists") from exc
    db.refresh(family)
    return get_family(db, family.id, context)


def delete_family(db: Session, family_id: UUID, context: AuthorizationContext) -> None:
    family = get_family(db, family_id, context)
    FamilyRepository(db).soft_delete(family)
    record_audit_event(db, "family.deleted", context.user_id, "Family", family.id)
    db.commit()
