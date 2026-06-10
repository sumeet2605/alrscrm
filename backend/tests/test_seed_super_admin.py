from app.identity.models import User
from sqlalchemy.orm import Session


def test_seed_super_admin_is_idempotent(db: Session, monkeypatch) -> None:
    from scripts import seed_super_admin

    monkeypatch.setattr(seed_super_admin, "SessionLocal", lambda: db)

    seed_super_admin.main()
    seed_super_admin.main()

    users = db.query(User).filter(User.email == seed_super_admin.ADMIN_EMAIL).all()
    assert len(users) == 1
    assert users[0].username == seed_super_admin.ADMIN_USERNAME
    assert users[0].is_active is True
    assert "Super Admin" in {role.name for role in users[0].roles}
