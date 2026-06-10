from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.identity.models import Branch, Organization
from app.identity.policies import AuthorizationContext, ensure_can_access_branch
from app.identity.schemas import BranchCreate, BranchUpdate
from app.shared.exceptions.application import ConflictError, ForbiddenError, NotFoundError
from app.shared.pagination import PageResult, paginate_query
from app.shared.services.audit_service import record_audit_event


def _normalize_code(code: str) -> str:
    return code.strip().upper()


def list_branches(
    db: Session, context: AuthorizationContext | None = None, page: int = 1, page_size: int = 50
) -> PageResult:
    query = db.query(Branch)
    if context is not None and not context.is_platform_admin:
        query = query.filter(Branch.organization_id == context.organization_id)
        if context.is_branch_scoped:
            query = query.filter(Branch.id == context.branch_id)
    return paginate_query(query.order_by(Branch.name), page, page_size)


def get_branch(db: Session, branch_id: UUID, context: AuthorizationContext | None = None) -> Branch:
    branch = db.get(Branch, branch_id)
    if branch is None:
        raise NotFoundError("Branch not found")
    ensure_can_access_branch(context, branch)
    return branch


def _ensure_organization(db: Session, organization_id: UUID) -> None:
    if db.get(Organization, organization_id) is None:
        raise NotFoundError("Organization not found")


def create_branch(
    db: Session, payload: BranchCreate, context: AuthorizationContext | None = None
) -> Branch:
    _ensure_organization(db, payload.organization_id)
    if context is not None and not context.is_platform_admin:
        if payload.organization_id != context.organization_id:
            raise ForbiddenError("Branch organization is outside the caller scope")
        if context.is_branch_scoped:
            raise ForbiddenError("Branch-scoped users cannot create branches")
    data = payload.model_dump()
    data["code"] = _normalize_code(data["code"])
    branch = Branch(**data)
    db.add(branch)
    try:
        record_audit_event(db, "branch.created", context.user_id if context else None, "Branch")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Branch code already exists for this organization") from exc
    db.refresh(branch)
    return branch


def update_branch(
    db: Session,
    branch_id: UUID,
    payload: BranchUpdate,
    context: AuthorizationContext | None = None,
) -> Branch:
    branch = get_branch(db, branch_id, context)
    data = payload.model_dump(exclude_unset=True)
    if "organization_id" in data:
        _ensure_organization(db, data["organization_id"])
        if context is not None and not context.is_platform_admin:
            if data["organization_id"] != context.organization_id:
                raise ForbiddenError("Branch organization is outside the caller scope")
            if context.is_branch_scoped:
                raise ForbiddenError("Branch-scoped users cannot reassign branches")
    for field, value in data.items():
        if field == "code" and value is not None:
            value = _normalize_code(value)
        setattr(branch, field, value)
    try:
        record_audit_event(
            db, "branch.updated", context.user_id if context else None, "Branch", branch.id
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Branch code already exists for this organization") from exc
    db.refresh(branch)
    return branch


def delete_branch(
    db: Session, branch_id: UUID, context: AuthorizationContext | None = None
) -> None:
    branch = get_branch(db, branch_id, context)
    branch.is_active = False
    record_audit_event(
        db,
        "branch.deactivated",
        context.user_id if context else None,
        "Branch",
        branch.id,
    )
    db.commit()
