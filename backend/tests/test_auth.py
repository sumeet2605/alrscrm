from app.core.security import decode_token, hash_password
from app.identity.models import Organization, Role, User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_login_refresh_and_me(client: TestClient, admin_user: User) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "organization_code": admin_user.organization.code,
            "email": admin_user.email,
            "password": "StrongPass123",
        },
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["success"] is True
    assert login_data["data"]["access_token"]
    assert login_data["data"]["refresh_token"]
    payload = decode_token(login_data["data"]["access_token"], "access")
    assert payload["organization_id"] == str(admin_user.organization_id)
    assert payload["branch_id"] is None

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_data['data']['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["data"]["email"] == admin_user.email

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["data"]["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["data"]["access_token"]

    replay_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["data"]["refresh_token"]},
    )
    assert replay_response.status_code == 401


def test_login_rejects_bad_password(client: TestClient, admin_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "organization_code": admin_user.organization.code,
            "email": admin_user.email,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_logout_revokes_refresh_token(client: TestClient, admin_user: User) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "organization_code": admin_user.organization.code,
            "email": admin_user.email,
            "password": "StrongPass123",
        },
    )
    refresh_token = login_response.json()["data"]["refresh_token"]

    logout_response = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 200

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401


def test_login_requires_organization_code(client: TestClient, admin_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "StrongPass123"},
    )

    assert response.status_code == 422


def test_duplicate_email_login_is_scoped_by_organization(client: TestClient, db: Session) -> None:
    role = db.query(Role).filter(Role.name == "Owner").one()
    org_a = Organization(name="Tenant A", code="TENA", is_active=True)
    org_b = Organization(name="Tenant B", code="TENB", is_active=True)
    user_a = User(
        organization=org_a,
        email="shared@example.com",
        password_hash=hash_password("TenantAPass123"),
        first_name="Tenant",
        last_name="A",
        is_active=True,
        roles=[role],
    )
    user_b = User(
        organization=org_b,
        email="shared@example.com",
        password_hash=hash_password("TenantBPass123"),
        first_name="Tenant",
        last_name="B",
        is_active=True,
        roles=[role],
    )
    db.add_all([org_a, org_b, user_a, user_b])
    db.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "organization_code": "TENB",
            "email": "shared@example.com",
            "password": "TenantBPass123",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["user"]["organization_id"] == str(org_b.id)

    wrong_tenant_response = client.post(
        "/api/v1/auth/login",
        json={
            "organization_code": "TENA",
            "email": "shared@example.com",
            "password": "TenantBPass123",
        },
    )
    assert wrong_tenant_response.status_code == 401


def test_password_policy_rejects_weak_password(
    client: TestClient, auth_headers: dict[str, str], admin_user: User
) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "organization_id": str(admin_user.organization_id),
            "email": "weak@example.com",
            "password": "weakpass",
            "first_name": "Weak",
            "last_name": "Password",
            "role_ids": [],
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
