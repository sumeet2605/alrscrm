from app.identity.models import Role, User
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

    get_response = client.get(f"/api/v1/organizations/{created['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["data"]["is_active"] is False


def test_roles_and_permissions_are_seeded(client: TestClient, auth_headers: dict[str, str]) -> None:
    roles_response = client.get("/api/v1/roles", headers=auth_headers)
    permissions_response = client.get("/api/v1/permissions", headers=auth_headers)

    assert roles_response.status_code == 200
    assert permissions_response.status_code == 200
    role_names = {role["name"] for role in roles_response.json()["data"]}
    permission_codes = {permission["code"] for permission in permissions_response.json()["data"]}
    assert "Super Admin" in role_names
    assert "Organization Admin" in role_names
    assert "identity:users:write" in permission_codes
    assert "galleries:reopen" in permission_codes
    assert "editing:view" in permission_codes
    assert "editing:approve" in permission_codes

    role_permissions = {
        role["name"]: {permission["code"] for permission in role["permissions"]}
        for role in roles_response.json()["data"]
    }
    assert "galleries:reopen" in role_permissions["Super Admin"]
    assert "galleries:reopen" in role_permissions["Organization Admin"]
    assert "galleries:reopen" in role_permissions["Branch Manager"]
    assert "editing:approve" in role_permissions["Organization Admin"]
    assert "editing:approve" in role_permissions["Branch Manager"]
    assert "editing:update" in role_permissions["Editor"]
    assert "editing:approve" not in role_permissions["Editor"]


def test_protected_endpoint_requires_token(client: TestClient) -> None:
    response = client.get("/api/v1/organizations")

    assert response.status_code == 401


def test_list_endpoints_include_pagination_meta(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/v1/organizations?page=1&page_size=10", headers=auth_headers)

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["meta"]["page"] == 1
    assert response.json()["meta"]["page_size"] == 10


def test_owner_cannot_see_other_organization(
    client: TestClient,
    auth_headers: dict[str, str],
    owner_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/organizations",
        json={"name": "Outside Studio", "code": "OUT", "is_active": True},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    outside_org_id = create_response.json()["data"]["id"]

    get_response = client.get(f"/api/v1/organizations/{outside_org_id}", headers=owner_headers)

    assert get_response.status_code == 403


def test_owner_cannot_assign_platform_role(
    client: TestClient,
    owner_headers: dict[str, str],
    owner_user: User,
    db,
) -> None:
    super_admin_role = db.query(Role).filter(Role.name == "Super Admin").one()
    response = client.post(
        "/api/v1/users",
        json={
            "organization_id": str(owner_user.organization_id),
            "branch_id": str(owner_user.branch_id),
            "email": "escalation@example.com",
            "password": "StrongPass123",
            "first_name": "Role",
            "last_name": "Escalation",
            "role_ids": [str(super_admin_role.id)],
        },
        headers=owner_headers,
    )

    assert response.status_code == 403


def test_cross_organization_branch_assignment_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
    admin_user: User,
    owner_user: User,
) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "organization_id": str(admin_user.organization_id),
            "branch_id": str(owner_user.branch_id),
            "email": "wrongbranch@example.com",
            "password": "StrongPass123",
            "first_name": "Wrong",
            "last_name": "Branch",
            "role_ids": [],
        },
        headers=auth_headers,
    )

    assert response.status_code == 403
