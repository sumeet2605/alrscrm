import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.identity.models import Organization, Role, User
from app.identity.seeds import seed_identity
from app.main import app

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
def auth_headers(client: TestClient, admin_user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "StrongPass123"},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
