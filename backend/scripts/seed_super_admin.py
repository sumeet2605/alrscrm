import os

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.identity.models import Branch, Organization, OrganizationSettings, Role, User
from app.identity.seeds import seed_identity

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "Admin@123"
PLATFORM_ORGANIZATION_CODE = "ALRSCRM"
LEGACY_ORGANIZATION_CODE = "ALRS"
PLATFORM_ORGANIZATION_NAME = "ALRSCRM"
PLATFORM_BRANCH_CODE = "PLATFORM"
PLATFORM_BRANCH_NAME = "Platform"
SAMPLE_ORGANIZATION_CODE = "ALS"
SAMPLE_ORGANIZATION_NAME = "Alluring Lens Studios"
SAMPLE_BRANCH_CODE = "MAIN"
SAMPLE_BRANCH_NAME = "Main Studio"
SAMPLE_OWNER_EMAIL = "owner@alluringlens.com"
SAMPLE_OWNER_PASSWORD = "Owner@123"


def _get_or_create_settings(db, organization: Organization) -> OrganizationSettings:
    settings = (
        db.query(OrganizationSettings)
        .filter(OrganizationSettings.organization_id == organization.id)
        .one_or_none()
    )
    if settings is None:
        settings = OrganizationSettings(
            organization=organization,
            studio_name=organization.name,
            timezone="Asia/Kolkata",
            currency="INR",
            delivery_expiry_default=30,
            gallery_selection_default_limit=30,
        )
        db.add(settings)
    return settings


def _get_or_create_organization(
    db,
    *,
    name: str,
    code: str,
    legacy_code: str | None = None,
) -> Organization:
    organization = db.query(Organization).filter(Organization.code == code).one_or_none()
    if organization is None and legacy_code is not None:
        organization = db.query(Organization).filter(Organization.code == legacy_code).one_or_none()
    if organization is None:
        organization = Organization(name=name, code=code, is_active=True)
        db.add(organization)
        db.flush()
    else:
        organization.name = name
        organization.code = code
        organization.is_active = True
    settings = _get_or_create_settings(db, organization)
    settings.studio_name = name
    return organization


def _get_or_create_branch(db, organization: Organization, *, name: str, code: str) -> Branch:
    branch = (
        db.query(Branch)
        .filter(Branch.organization_id == organization.id, Branch.code == code)
        .one_or_none()
    )
    if branch is None:
        branch = Branch(
            organization=organization,
            name=name,
            code=code,
            city=name,
            is_active=True,
        )
        db.add(branch)
        db.flush()
    else:
        branch.name = name
        branch.city = branch.city or name
        branch.is_active = True
    return branch


def _get_role(db, name: str) -> Role:
    return db.query(Role).filter(Role.name == name).one()


def _ensure_user(
    db,
    *,
    organization: Organization,
    branch: Branch,
    role: Role,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    username: str | None = None,
) -> User:
    user = (
        db.query(User)
        .filter(User.organization_id == organization.id, User.email == email)
        .one_or_none()
    )
    if user is None:
        user = User(
            organization=organization,
            branch=branch,
            username=username,
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            roles=[role],
        )
        db.add(user)
    else:
        user.organization = organization
        user.branch = branch
        user.username = username
        user.password_hash = hash_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        if role not in user.roles:
            user.roles.append(role)
    return user


def main() -> None:
    db = SessionLocal()
    try:
        seed_identity(db)
        organization = _get_or_create_organization(
            db,
            name=PLATFORM_ORGANIZATION_NAME,
            code=PLATFORM_ORGANIZATION_CODE,
            legacy_code=LEGACY_ORGANIZATION_CODE,
        )
        platform_branch = _get_or_create_branch(
            db, organization, name=PLATFORM_BRANCH_NAME, code=PLATFORM_BRANCH_CODE
        )
        super_admin_role = _get_role(db, "Super Admin")
        _ensure_user(
            db,
            organization=organization,
            branch=platform_branch,
            role=super_admin_role,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            first_name="Admin",
            last_name="User",
            username=ADMIN_USERNAME,
        )

        if os.getenv("SEED_SAMPLE_TENANT", "false").lower() == "true":
            sample_organization = _get_or_create_organization(
                db,
                name=SAMPLE_ORGANIZATION_NAME,
                code=SAMPLE_ORGANIZATION_CODE,
            )
            sample_branch = _get_or_create_branch(
                db,
                sample_organization,
                name=SAMPLE_BRANCH_NAME,
                code=SAMPLE_BRANCH_CODE,
            )
            owner_role = _get_role(db, "Owner")
            _ensure_user(
                db,
                organization=sample_organization,
                branch=sample_branch,
                role=owner_role,
                email=SAMPLE_OWNER_EMAIL,
                password=SAMPLE_OWNER_PASSWORD,
                first_name="Alluring",
                last_name="Owner",
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
