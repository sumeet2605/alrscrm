from uuid import uuid4

from app.core.security import create_access_token, hash_password
from app.identity.models import Branch, Organization, Role, User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _family_payload(organization_id: str, branch_id: str, phone: str = "+91 90000 00001") -> dict:
    return {
        "organization_id": organization_id,
        "branch_id": branch_id,
        "primary_contact_name": "Aarav Sharma",
        "primary_contact_phone": phone,
        "primary_contact_email": "aarav@example.com",
        "partner_name": "Mira Sharma",
        "partner_phone": "+91 90000 00002",
        "partner_email": "mira@example.com",
        "city": "Mumbai",
        "expected_delivery_date": "2026-08-15",
        "source": "INSTAGRAM",
        "notes": "Interested in newborn and maternity packages.",
        "status": "INTERESTED",
        "members": [
            {
                "name": "Mira Sharma",
                "relationship": "MOTHER",
                "date_of_birth": "1995-02-10",
                "gender": "FEMALE",
            }
        ],
        "address": {
            "address_line_1": "101 Studio Lane",
            "address_line_2": "Bandra West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "postal_code": "400050",
        },
        "service_interests": [
            {"service_type": "MATERNITY", "priority": 1, "notes": "Due in August"},
            {"service_type": "NEWBORN", "priority": 2, "notes": None},
        ],
    }


def _create_user_with_role(
    db: Session,
    organization: Organization,
    branch: Branch,
    role_name: str,
    email: str,
) -> User:
    role = db.query(Role).filter(Role.name == role_name).one()
    user = User(
        organization=organization,
        branch=branch,
        email=email,
        password_hash=hash_password("StrongPass123"),
        first_name=role_name.split()[0],
        last_name="User",
        is_active=True,
        roles=[role],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_family_crud_search_and_soft_delete(
    client: TestClient,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch_id is not None
    payload = _family_payload(str(owner_user.organization_id), str(owner_user.branch_id))

    create_response = client.post("/api/v1/families", json=payload, headers=owner_headers)
    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["family_code"] == "ALS-000001"
    assert created["primary_contact_phone"] == "+91 90000 00001"
    assert len(created["members"]) == 1
    assert len(created["service_interests"]) == 2

    list_response = client.get("/api/v1/families?search=Aarav", headers=owner_headers)
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total"] == 1

    search_response = client.get("/api/v1/families/search?phone=90000", headers=owner_headers)
    assert search_response.status_code == 200
    assert search_response.json()["data"][0]["id"] == created["id"]

    update_response = client.put(
        f"/api/v1/families/{created['id']}",
        json={
            "status": "BOOKED",
            "address": {
                "address_line_1": "202 Updated Studio Lane",
                "address_line_2": "Bandra East",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400051",
            },
            "members": [
                {
                    "name": "Baby Sharma",
                    "relationship": "BABY",
                    "date_of_birth": None,
                    "gender": "OTHER",
                }
            ],
        },
        headers=owner_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["status"] == "BOOKED"
    assert update_response.json()["data"]["members"][0]["relationship"] == "BABY"
    assert update_response.json()["data"]["address"]["address_line_1"] == "202 Updated Studio Lane"

    second_address_update = client.put(
        f"/api/v1/families/{created['id']}",
        json={
            "address": {
                "address_line_1": "303 Final Studio Lane",
                "address_line_2": "Bandra East",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400052",
            }
        },
        headers=owner_headers,
    )
    assert second_address_update.status_code == 200
    assert (
        second_address_update.json()["data"]["address"]["address_line_1"] == "303 Final Studio Lane"
    )

    delete_response = client.delete(f"/api/v1/families/{created['id']}", headers=owner_headers)
    assert delete_response.status_code == 200

    get_response = client.get(f"/api/v1/families/{created['id']}", headers=owner_headers)
    assert get_response.status_code == 404


def test_family_primary_phone_must_be_unique(
    client: TestClient,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch_id is not None
    payload = _family_payload(str(owner_user.organization_id), str(owner_user.branch_id))

    first_response = client.post("/api/v1/families", json=payload, headers=owner_headers)
    assert first_response.status_code == 201

    duplicate_response = client.post("/api/v1/families", json=payload, headers=owner_headers)
    assert duplicate_response.status_code == 409


def test_sales_can_write_but_cannot_delete_family(client: TestClient, db: Session) -> None:
    organization = Organization(name="Sales Studio", code=f"SLS-{uuid4()}", is_active=True)
    branch = Branch(
        organization=organization,
        name="Sales Branch",
        code="SLS-BR",
        city="Delhi",
        is_active=True,
    )
    db.add(organization)
    db.commit()
    sales = _create_user_with_role(
        db,
        organization,
        branch,
        "Sales Executive",
        "sales@example.com",
    )
    headers = {"Authorization": f"Bearer {create_access_token(sales.id)}"}
    payload = _family_payload(str(organization.id), str(branch.id), "+91 98888 00001")

    create_response = client.post("/api/v1/families", json=payload, headers=headers)
    assert create_response.status_code == 201
    family_id = create_response.json()["data"]["id"]

    update_response = client.put(
        f"/api/v1/families/{family_id}",
        json={"status": "ACTIVE"},
        headers=headers,
    )
    assert update_response.status_code == 200

    delete_response = client.delete(f"/api/v1/families/{family_id}", headers=headers)
    assert delete_response.status_code == 403
