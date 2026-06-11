from uuid import UUID

from app.core.crypto import decrypt_json
from app.core.security import create_access_token, hash_password
from app.identity.models import Branch, Organization, Role, User
from app.integrations.models import OrganizationIntegration
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _create_user(db: Session, organization: Organization, branch: Branch, email: str) -> User:
    role = db.query(Role).filter(Role.name == "Owner").one()
    user = User(
        organization=organization,
        branch=branch,
        email=email,
        password_hash=hash_password("StrongPass123"),
        first_name="Owner",
        last_name="Integration",
        is_active=True,
        roles=[role],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _fixture(db: Session):
    organization = Organization(name="Integration Studio", code="INT", is_active=True)
    branch = Branch(
        organization=organization,
        name="Integration Branch",
        code="INT-BR",
        city="Mumbai",
        is_active=True,
    )
    other_organization = Organization(name="Other Integration Studio", code="OINT", is_active=True)
    other_branch = Branch(
        organization=other_organization,
        name="Other Branch",
        code="OINT-BR",
        city="Delhi",
        is_active=True,
    )
    db.add_all([organization, other_organization])
    db.commit()
    owner = _create_user(db, organization, branch, "owner@integrations.example.com")
    other_owner = _create_user(
        db, other_organization, other_branch, "other@integrations.example.com"
    )
    return organization, branch, owner, other_owner


def test_integration_create_verify_health_and_encryption(client: TestClient, db: Session) -> None:
    organization, branch, owner, _ = _fixture(db)
    response = client.post(
        "/api/v1/integrations",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "provider": "SMTP_EMAIL",
            "credentials": {
                "host": "smtp.example.com",
                "port": 587,
                "username": "mailer",
                "password": "smtp-secret",
                "from_email": "studio@example.com",
            },
        },
        headers=_headers(owner),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "DISCONNECTED"
    assert sorted(data["credential_keys"]) == [
        "from_email",
        "host",
        "password",
        "port",
        "username",
    ]

    stored = db.get(OrganizationIntegration, UUID(data["id"]))
    assert stored is not None
    assert "smtp-secret" not in stored.encrypted_credentials
    assert decrypt_json(stored.encrypted_credentials)["password"] == "smtp-secret"

    verify_response = client.post(
        f"/api/v1/integrations/{data['id']}/verify",
        headers=_headers(owner),
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["data"]["status"] == "CONNECTED"
    assert verify_response.json()["data"]["last_verified_at"] is not None

    health_response = client.get("/api/v1/integrations/health", headers=_headers(owner))
    assert health_response.status_code == 200
    assert health_response.json()["data"]["connected"] == 1
    assert health_response.json()["data"]["disconnected"] == 0


def test_integration_access_is_tenant_scoped(client: TestClient, db: Session) -> None:
    organization, branch, owner, other_owner = _fixture(db)
    create_response = client.post(
        "/api/v1/integrations",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "provider": "AWS_S3",
            "credentials": {
                "bucket": "tenant-bucket",
                "region": "ap-south-1",
                "access_key_id": "key",
                "secret_access_key": "secret",
            },
        },
        headers=_headers(owner),
    )
    assert create_response.status_code == 201
    integration_id = create_response.json()["data"]["id"]

    list_response = client.get("/api/v1/integrations", headers=_headers(other_owner))
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total"] == 0

    verify_response = client.post(
        f"/api/v1/integrations/{integration_id}/verify",
        headers=_headers(other_owner),
    )
    assert verify_response.status_code == 403
