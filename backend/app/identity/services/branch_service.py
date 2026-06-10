from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.identity.models import Branch, Organization
from app.identity.schemas import BranchCreate, BranchUpdate
from app.shared.exceptions.http import conflict, not_found


def list_branches(db: Session) -> list[Branch]:
    return db.query(Branch).order_by(Branch.name).all()


def get_branch(db: Session, branch_id: UUID) -> Branch:
    branch = db.get(Branch, branch_id)
    if branch is None:
        raise not_found("Branch not found")
    return branch


def _ensure_organization(db: Session, organization_id: UUID) -> None:
    if db.get(Organization, organization_id) is None:
        raise not_found("Organization not found")


def create_branch(db: Session, payload: BranchCreate) -> Branch:
    _ensure_organization(db, payload.organization_id)
    branch = Branch(**payload.model_dump())
    db.add(branch)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Branch code already exists for this organization") from exc
    db.refresh(branch)
    return branch


def update_branch(db: Session, branch_id: UUID, payload: BranchUpdate) -> Branch:
    branch = get_branch(db, branch_id)
    data = payload.model_dump(exclude_unset=True)
    if "organization_id" in data:
        _ensure_organization(db, data["organization_id"])
    for field, value in data.items():
        setattr(branch, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Branch code already exists for this organization") from exc
    db.refresh(branch)
    return branch


def delete_branch(db: Session, branch_id: UUID) -> None:
    branch = get_branch(db, branch_id)
    db.delete(branch)
    db.commit()
