from fastapi.testclient import TestClient


def test_organization_crud(client: TestClient, auth_headers: dict[str, str]) -> None:
    create_response = client.post(
        "/api/v1/organizations",
        json={"name": "Mumbai Studio", "code": "MUM", "is_active": True},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()["data"]

    list_response = client.get("/api/v1/organizations", headers=auth_headers)
    assert list_response.status_code == 200
    assert any(item["code"] == "MUM" for item in list_response.json()["data"])

    update_response = client.patch(
        f"/api/v1/organizations/{created['id']}",
        json={"name": "Mumbai Flagship Studio"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == "Mumbai Flagship Studio"

    delete_response = client.delete(f"/api/v1/organizations/{created['id']}", headers=auth_headers)
    assert delete_response.status_code == 200


def test_roles_and_permissions_are_seeded(client: TestClient, auth_headers: dict[str, str]) -> None:
    roles_response = client.get("/api/v1/roles", headers=auth_headers)
    permissions_response = client.get("/api/v1/permissions", headers=auth_headers)

    assert roles_response.status_code == 200
    assert permissions_response.status_code == 200
    role_names = {role["name"] for role in roles_response.json()["data"]}
    permission_codes = {permission["code"] for permission in permissions_response.json()["data"]}
    assert "Super Admin" in role_names
    assert "identity:users:write" in permission_codes


def test_protected_endpoint_requires_token(client: TestClient) -> None:
    response = client.get("/api/v1/organizations")

    assert response.status_code == 401
