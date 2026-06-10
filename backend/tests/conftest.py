import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.identity.models import Branch, Organization, Role, User
from app.identity.seeds import seed_identity
from app.main import app
from app.sales.seeds import seed_sales

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture()
def db() -> Generator[Session]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        seed_identity(session)
        seed_sales(session)
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db: Session) -> User:
    organization = Organization(name="ALR Studio", code="ALR", is_active=True)
    role = db.query(Role).filter(Role.name == "Super Admin").one()
    user = User(
        organization=organization,
        email="owner@example.com",
        password_hash=hash_password("StrongPass123"),
        first_name="Studio",
        last_name="Owner",
        is_active=True,
        roles=[role],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def owner_user(db: Session) -> User:
    organization = Organization(name="Tenant Studio", code="TEN", is_active=True)
    branch = Branch(
        organization=organization,
        name="Tenant Branch",
        code="TEN-BR",
        city="Mumbai",
        is_active=True,
    )
    role = db.query(Role).filter(Role.name == "Owner").one()
    user = User(
        organization=organization,
        branch=branch,
        email="owner2@example.com",
        password_hash=hash_password("StrongPass123"),
        first_name="Tenant",
        last_name="Owner",
        is_active=True,
        roles=[role],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def owner_headers(owner_user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(owner_user.id)}"}


@pytest.fixture()
def auth_headers(client: TestClient, admin_user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "StrongPass123"},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
