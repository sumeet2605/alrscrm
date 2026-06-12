from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth.models import RefreshTokenSession
from app.core.security import hash_password
from app.identity.models import Branch, Organization, Role, User
from app.identity.policies import (
    AuthorizationContext,
    ensure_can_access_user,
    ensure_can_assign_roles,
)
from app.identity.schemas import UserCreate, UserUpdate
from app.shared.exceptions.application import ConflictError, ForbiddenError, NotFoundError
from app.shared.pagination import PageResult, paginate_query
from app.shared.services.audit_service import record_audit_event


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_username(username: str | None) -> str | None:
    if username is None:
        return None
    normalized = username.strip().lower()
    return normalized or None


def list_users(
    db: Session, context: AuthorizationContext | None = None, page: int = 1, page_size: int = 50
) -> PageResult:
    query = db.query(User).options(selectinload(User.roles).selectinload(Role.permissions))
    if context is not None and not context.is_platform_admin:
        query = query.filter(User.organization_id == context.organization_id)
        if context.is_branch_scoped:
            query = query.filter(User.branch_id == context.branch_id)
    return paginate_query(query.order_by(User.email), page, page_size)


def get_user(db: Session, user_id: UUID, context: AuthorizationContext | None = None) -> User:
    user = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.id == user_id)
        .one_or_none()
    )
    if user is None:
        raise NotFoundError("User not found")
    ensure_can_access_user(context, user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.email == _normalize_email(email))
        .one_or_none()
    )


def get_user_by_organization_email(db: Session, organization_id: UUID, email: str) -> User | None:
    return (
        db.query(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(
            User.organization_id == organization_id,
            User.email == _normalize_email(email),
        )
        .one_or_none()
    )


def _ensure_user_refs(db: Session, organization_id: UUID, branch_id: UUID | None) -> None:
    if db.get(Organization, organization_id) is None:
        raise NotFoundError("Organization not found")
    if branch_id is not None:
        branch = db.get(Branch, branch_id)
        if branch is None:
            raise NotFoundError("Branch not found")
        if branch.organization_id != organization_id:
            raise ForbiddenError("Branch does not belong to the selected organization")


def _load_roles(db: Session, role_ids: list[UUID]) -> list[Role]:
    if not role_ids:
        return []
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    if len(roles) != len(set(role_ids)):
        raise NotFoundError("Role not found")
    return roles


def create_user(
    db: Session, payload: UserCreate, context: AuthorizationContext | None = None
) -> User:
    _ensure_user_refs(db, payload.organization_id, payload.branch_id)
    roles = _load_roles(db, payload.role_ids)
    ensure_can_assign_roles(context, roles)
    if context is not None and not context.is_platform_admin:
        if payload.organization_id != context.organization_id:
            raise ForbiddenError("User organization is outside the caller scope")
        if context.is_branch_scoped and payload.branch_id != context.branch_id:
            raise ForbiddenError("User branch is outside the caller scope")
    data = payload.model_dump(exclude={"password", "role_ids"})
    data["email"] = _normalize_email(data["email"])
    data["username"] = _normalize_username(data.get("username"))
    user = User(**data, password_hash=hash_password(payload.password))
    user.roles = roles
    db.add(user)
    try:
        record_audit_event(db, "user.created", context.user_id if context else None, "User")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("User email already exists for this organization") from exc
    db.refresh(user)
    return get_user(db, user.id, context)


def update_user(
    db: Session, user_id: UUID, payload: UserUpdate, context: AuthorizationContext | None = None
) -> User:
    user = get_user(db, user_id, context)
    data = payload.model_dump(exclude_unset=True)
    organization_id = data.get("organization_id", user.organization_id)
    branch_id = data.get("branch_id", user.branch_id)
    if "organization_id" in data or "branch_id" in data:
        _ensure_user_refs(db, organization_id, branch_id)
    if "role_ids" in data:
        roles = _load_roles(db, data.pop("role_ids") or [])
        ensure_can_assign_roles(context, roles)
        user.roles = roles
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))
        _revoke_user_sessions(db, user.id)
    if "email" in data and data["email"] is not None:
        data["email"] = _normalize_email(data["email"])
    if "username" in data:
        data["username"] = _normalize_username(data["username"])
    if context is not None and not context.is_platform_admin:
        if organization_id != context.organization_id:
            raise ForbiddenError("User organization is outside the caller scope")
        if context.is_branch_scoped and branch_id != context.branch_id:
            raise ForbiddenError("User branch is outside the caller scope")
    for field, value in data.items():
        setattr(user, field, value)
    try:
        record_audit_event(
            db, "user.updated", context.user_id if context else None, "User", user.id
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("User email already exists for this organization") from exc
    return get_user(db, user.id, context)


def delete_user(db: Session, user_id: UUID, context: AuthorizationContext | None = None) -> None:
    user = get_user(db, user_id, context)
    user.is_active = False
    _revoke_user_sessions(db, user.id)
    record_audit_event(
        db, "user.deactivated", context.user_id if context else None, "User", user.id
    )
    db.commit()


def _revoke_user_sessions(db: Session, user_id: UUID) -> None:
    now = datetime.now(UTC)
    db.query(RefreshTokenSession).filter(
        RefreshTokenSession.user_id == user_id,
        RefreshTokenSession.revoked_at.is_(None),
    ).update({"revoked_at": now})
