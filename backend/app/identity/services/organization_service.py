from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.identity.models import Organization
from app.identity.schemas import OrganizationCreate, OrganizationUpdate
from app.shared.exceptions.http import conflict, not_found


def list_organizations(db: Session) -> list[Organization]:
    return db.query(Organization).order_by(Organization.name).all()


def get_organization(db: Session, organization_id: UUID) -> Organization:
    organization = db.get(Organization, organization_id)
    if organization is None:
        raise not_found("Organization not found")
    return organization


def create_organization(db: Session, payload: OrganizationCreate) -> Organization:
    organization = Organization(**payload.model_dump())
    db.add(organization)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Organization code already exists") from exc
    db.refresh(organization)
    return organization


def update_organization(
    db: Session, organization_id: UUID, payload: OrganizationUpdate
) -> Organization:
    organization = get_organization(db, organization_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(organization, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("Organization code already exists") from exc
    db.refresh(organization)
    return organization


def delete_organization(db: Session, organization_id: UUID) -> None:
    organization = get_organization(db, organization_id)
    db.delete(organization)
    db.commit()
