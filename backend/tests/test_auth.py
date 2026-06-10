from app.identity.models import User
from fastapi.testclient import TestClient


def test_login_refresh_and_me(client: TestClient, admin_user: User) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "StrongPass123"},
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["success"] is True
    assert login_data["data"]["access_token"]
    assert login_data["data"]["refresh_token"]

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


def test_login_rejects_bad_password(client: TestClient, admin_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "wrong-password"},
    )

    assert response.status_code == 401
