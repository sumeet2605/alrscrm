from app.core.database import SessionLocal
from app.core.security import hash_password
from app.identity.models import Organization, Role, User
from app.identity.seeds import seed_identity

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_ORGANIZATION_CODE = "ALRS"


def main() -> None:
    db = SessionLocal()
    try:
        seed_identity(db)
        organization = (
            db.query(Organization)
            .filter(Organization.code == ADMIN_ORGANIZATION_CODE)
            .one_or_none()
        )
        if organization is None:
            organization = Organization(
                name="ALRSCRM",
                code=ADMIN_ORGANIZATION_CODE,
                is_active=True,
            )
            db.add(organization)
            db.flush()

        super_admin_role = db.query(Role).filter(Role.name == "Super Admin").one()
        user = db.query(User).filter(User.email == ADMIN_EMAIL).one_or_none()
        if user is None:
            user = User(
                organization_id=organization.id,
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password_hash=hash_password(ADMIN_PASSWORD),
                first_name="Admin",
                last_name="User",
                is_active=True,
                roles=[super_admin_role],
            )
            db.add(user)
        else:
            user.organization_id = organization.id
            user.username = ADMIN_USERNAME
            user.password_hash = hash_password(ADMIN_PASSWORD)
            user.first_name = "Admin"
            user.last_name = "User"
            user.is_active = True
            if super_admin_role not in user.roles:
                user.roles.append(super_admin_role)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
