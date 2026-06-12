from uuid import UUID

from app.identity.models import Branch, Organization, Role, User
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
    assert "organizations:onboard" in permission_codes

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
    assert "organizations:onboard" in role_permissions["Super Admin"]
    assert "organizations:onboard" not in role_permissions["Organization Admin"]
    assert "organizations:create" not in role_permissions["Owner"]


def test_organization_onboarding_creates_tenant_branch_owner_and_settings(
    client: TestClient,
    auth_headers: dict[str, str],
    db,
) -> None:
    response = client.post(
        "/api/v1/organizations/onboard",
        json={
            "organization": {
                "name": "Little Smiles Photography",
                "code": "LSP",
                "timezone": "Asia/Kolkata",
                "email": "hello@littlesmiles.com",
                "phone": "+91 90000 10000",
            },
            "branch": {"name": "Main Studio"},
            "owner": {
                "name": "Little Owner",
                "email": "owner@littlesmiles.com",
                "phone": "+91 90000 10001",
            },
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()["data"]
    organization_id = data["organization"]["id"]
    branch_id = data["branch_id"]
    owner_id = data["owner_id"]
    temporary_password = data["owner_temporary_password"]

    organization = db.get(Organization, UUID(organization_id))
    branch = db.get(Branch, UUID(branch_id))
    owner = db.get(User, UUID(owner_id))

    assert organization is not None
    assert organization.code == "LSP"
    assert organization.settings is not None
    assert organization.settings.studio_name == "Little Smiles Photography"
    assert branch is not None
    assert branch.organization_id == organization.id
    assert branch.name == "Main Studio"
    assert owner is not None
    assert owner.organization_id == organization.id
    assert owner.branch_id == branch.id
    assert "Owner" in {role.name for role in owner.roles}
    assert len(temporary_password) >= 8


def test_organization_onboarding_rejects_duplicate_org_code(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {
        "organization": {
            "name": "Duplicate Studio",
            "code": "DUP",
            "timezone": "Asia/Kolkata",
            "email": "hello@duplicate.com",
            "phone": "+91 90000 20000",
        },
        "branch": {"name": "Main Studio"},
        "owner": {
            "name": "Duplicate Owner",
            "email": "owner@duplicate.com",
            "phone": "+91 90000 20001",
        },
    }

    first = client.post("/api/v1/organizations/onboard", json=payload, headers=auth_headers)
    second = client.post("/api/v1/organizations/onboard", json=payload, headers=auth_headers)

    assert first.status_code == 201
    assert second.status_code == 409


def test_organization_onboarding_does_not_create_children_when_org_code_conflicts(
    client: TestClient,
    auth_headers: dict[str, str],
    db,
) -> None:
    payload = {
        "organization": {
            "name": "Rollback Studio",
            "code": "RBK",
            "timezone": "Asia/Kolkata",
            "email": "hello@rollback.com",
            "phone": "+91 90000 30000",
        },
        "branch": {"name": "Main Studio"},
        "owner": {
            "name": "Rollback Owner",
            "email": "owner@rollback.com",
            "phone": "+91 90000 30001",
        },
    }
    first = client.post(
        "/api/v1/organizations/onboard",
        json=payload,
        headers=auth_headers,
    )
    branch_count = db.query(Branch).count()
    user_count = db.query(User).count()
    second = client.post(
        "/api/v1/organizations/onboard",
        json=payload,
        headers=auth_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert db.query(Branch).count() == branch_count
    assert db.query(User).count() == user_count


def test_organization_settings_can_be_updated(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/organizations",
        json={"name": "Settings Studio", "code": "SET", "is_active": True},
        headers=auth_headers,
    )
    organization_id = create_response.json()["data"]["id"]

    update_response = client.patch(
        f"/api/v1/organizations/{organization_id}/settings",
        json={
            "studio_name": "Settings Studio Premium",
            "contact_email": "hello@settings.com",
            "currency": "usd",
            "delivery_expiry_default": 45,
            "gallery_selection_default_limit": 80,
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()["data"]
    assert data["studio_name"] == "Settings Studio Premium"
    assert data["currency"] == "USD"
    assert data["delivery_expiry_default"] == 45


def test_non_platform_user_cannot_onboard_organization(
    client: TestClient,
    owner_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/organizations/onboard",
        json={
            "organization": {
                "name": "Blocked Studio",
                "code": "BLK",
                "timezone": "Asia/Kolkata",
            },
            "branch": {"name": "Main Studio"},
            "owner": {"name": "Blocked Owner", "email": "owner@blocked.com"},
        },
        headers=owner_headers,
    )

    assert response.status_code == 403


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
