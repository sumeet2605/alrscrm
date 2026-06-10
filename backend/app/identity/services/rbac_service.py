from sqlalchemy.orm import Session, selectinload

from app.identity.models import Permission, Role


def list_roles(db: Session) -> list[Role]:
    return db.query(Role).options(selectinload(Role.permissions)).order_by(Role.name).all()


def list_permissions(db: Session) -> list[Permission]:
    return db.query(Permission).order_by(Permission.code).all()
