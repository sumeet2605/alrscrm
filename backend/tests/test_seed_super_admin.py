from app.core.security import verify_password
from app.identity.models import Branch, Organization, User
from sqlalchemy.orm import Session


def test_seed_super_admin_is_idempotent(db: Session, monkeypatch) -> None:
    from scripts import seed_super_admin

    monkeypatch.setattr(seed_super_admin, "SessionLocal", lambda: db)
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "LocalStrongPass123")

    seed_super_admin.main()
    user = db.query(User).filter(User.email == seed_super_admin.ADMIN_EMAIL).one()
    user.password_hash = "existing-hash"
    user.password_reset_required = False
    db.commit()
    seed_super_admin.main()

    users = db.query(User).filter(User.email == seed_super_admin.ADMIN_EMAIL).all()
    assert len(users) == 1
    assert users[0].username == seed_super_admin.ADMIN_USERNAME
    assert users[0].is_active is True
    assert users[0].organization.code == seed_super_admin.PLATFORM_ORGANIZATION_CODE
    assert users[0].organization.name == seed_super_admin.PLATFORM_ORGANIZATION_NAME
    assert users[0].branch is not None
    assert users[0].branch.code == seed_super_admin.PLATFORM_BRANCH_CODE
    assert "Super Admin" in {role.name for role in users[0].roles}
    assert users[0].password_hash == "existing-hash"
    assert users[0].password_reset_required is False


def test_seed_super_admin_does_not_create_sample_tenant_by_default(
    db: Session, monkeypatch
) -> None:
    from scripts import seed_super_admin

    monkeypatch.setattr(seed_super_admin, "SessionLocal", lambda: db)
    monkeypatch.delenv("SEED_SAMPLE_TENANT", raising=False)
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "LocalStrongPass123")

    seed_super_admin.main()

    sample = (
        db.query(Organization)
        .filter(Organization.code == seed_super_admin.SAMPLE_ORGANIZATION_CODE)
        .one_or_none()
    )
    assert sample is None


def test_seed_super_admin_can_create_sample_tenant(db: Session, monkeypatch) -> None:
    from scripts import seed_super_admin

    monkeypatch.setattr(seed_super_admin, "SessionLocal", lambda: db)
    monkeypatch.setenv("SEED_SAMPLE_TENANT", "true")
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "LocalStrongPass123")
    monkeypatch.setenv("SAMPLE_OWNER_PASSWORD", "OwnerLocalStrongPass123")

    seed_super_admin.main()
    seed_super_admin.main()

    sample = (
        db.query(Organization)
        .filter(Organization.code == seed_super_admin.SAMPLE_ORGANIZATION_CODE)
        .one()
    )
    branch_count = (
        db.query(Branch)
        .filter(
            Branch.organization_id == sample.id,
            Branch.code == seed_super_admin.SAMPLE_BRANCH_CODE,
        )
        .count()
    )
    owner_count = (
        db.query(User)
        .filter(
            User.organization_id == sample.id,
            User.email == seed_super_admin.SAMPLE_OWNER_EMAIL,
        )
        .count()
    )

    assert sample.name == seed_super_admin.SAMPLE_ORGANIZATION_NAME
    assert branch_count == 1
    assert owner_count == 1


def test_seed_super_admin_requires_password_for_new_user(db: Session, monkeypatch) -> None:
    from scripts import seed_super_admin

    monkeypatch.setattr(seed_super_admin, "SessionLocal", lambda: db)
    monkeypatch.delenv("BOOTSTRAP_ADMIN_PASSWORD", raising=False)

    try:
        seed_super_admin.main()
    except seed_super_admin.BootstrapConfigurationError as exc:
        assert "BOOTSTRAP_ADMIN_PASSWORD" in str(exc)
    else:
        raise AssertionError("Expected bootstrap configuration error")


def test_seed_super_admin_force_reset_requires_explicit_flag(db: Session, monkeypatch) -> None:
    from scripts import seed_super_admin

    monkeypatch.setattr(seed_super_admin, "SessionLocal", lambda: db)
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "InitialStrongPass123")
    seed_super_admin.main()
    user = db.query(User).filter(User.email == seed_super_admin.ADMIN_EMAIL).one()
    assert verify_password("InitialStrongPass123", user.password_hash)

    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "ResetStrongPass123")
    seed_super_admin.main()
    user = db.query(User).filter(User.email == seed_super_admin.ADMIN_EMAIL).one()
    assert verify_password("InitialStrongPass123", user.password_hash)

    monkeypatch.setenv("BOOTSTRAP_FORCE_PASSWORD_RESET", "true")
    seed_super_admin.main()
    user = db.query(User).filter(User.email == seed_super_admin.ADMIN_EMAIL).one()
    assert verify_password("ResetStrongPass123", user.password_hash)
    assert user.password_reset_required is True
