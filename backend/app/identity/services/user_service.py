from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.identity.models import Branch, Organization, Role, User
from app.identity.schemas import UserCreate, UserUpdate
from app.shared.exceptions.http import conflict, not_found


def list_users(db: Session) -> list[User]:
    return db.query(User).options(selectinload(User.roles)).order_by(User.email).all()


def get_user(db: Session, user_id: UUID) -> User:
    user = db.query(User).options(selectinload(User.roles)).filter(User.id == user_id).one_or_none()
    if user is None:
        raise not_found("User not found")
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.email == email)
        .one_or_none()
    )


def _ensure_user_refs(db: Session, organization_id: UUID, branch_id: UUID | None) -> None:
    if db.get(Organization, organization_id) is None:
        raise not_found("Organization not found")
    if branch_id is not None and db.get(Branch, branch_id) is None:
        raise not_found("Branch not found")


def _load_roles(db: Session, role_ids: list[UUID]) -> list[Role]:
    if not role_ids:
        return []
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    if len(roles) != len(set(role_ids)):
        raise not_found("Role not found")
    return roles


def create_user(db: Session, payload: UserCreate) -> User:
    _ensure_user_refs(db, payload.organization_id, payload.branch_id)
    roles = _load_roles(db, payload.role_ids)
    data = payload.model_dump(exclude={"password", "role_ids"})
    user = User(**data, password_hash=hash_password(payload.password))
    user.roles = roles
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("User email already exists for this organization") from exc
    db.refresh(user)
    return get_user(db, user.id)


def update_user(db: Session, user_id: UUID, payload: UserUpdate) -> User:
    user = get_user(db, user_id)
    data = payload.model_dump(exclude_unset=True)
    organization_id = data.get("organization_id", user.organization_id)
    branch_id = data.get("branch_id", user.branch_id)
    if "organization_id" in data or "branch_id" in data:
        _ensure_user_refs(db, organization_id, branch_id)
    if "role_ids" in data:
        user.roles = _load_roles(db, data.pop("role_ids") or [])
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))
    for field, value in data.items():
        setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("User email already exists for this organization") from exc
    return get_user(db, user.id)


def delete_user(db: Session, user_id: UUID) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
