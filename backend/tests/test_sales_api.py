from datetime import date, timedelta

from app.core.security import create_access_token, hash_password
from app.families.models import Family
from app.identity.models import Branch, Organization, Role, User
from app.sales.models import LostReason
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _create_family(db: Session, organization: Organization, branch: Branch) -> Family:
    family = Family(
        organization=organization,
        branch=branch,
        family_code="ALS-900001",
        primary_contact_name="Aarav Sharma",
        primary_contact_phone="+91 90000 00001",
        primary_contact_email="aarav@example.com",
        city="Mumbai",
        source="INSTAGRAM",
        status="INTERESTED",
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _create_user(db: Session, organization: Organization, branch: Branch, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).one()
    user = User(
        organization=organization,
        branch=branch,
        email=f"{role_name.lower().replace(' ', '.')}@example.com",
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


def _opportunity_payload(owner_user: User, family: Family) -> dict:
    return {
        "organization_id": str(owner_user.organization_id),
        "branch_id": str(owner_user.branch_id),
        "family_id": str(family.id),
        "assigned_to_user_id": str(owner_user.id),
        "opportunity_type": "NEWBORN",
        "current_stage": "PACKAGE_SENT",
        "estimated_value": "20000.00",
        "probability": 35,
        "expected_booking_date": str(date.today() + timedelta(days=10)),
        "notes": "Package shared on WhatsApp.",
    }


def test_opportunity_pipeline_followups_metrics_and_history(
    client: TestClient,
    db: Session,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch is not None
    family = _create_family(db, owner_user.organization, owner_user.branch)

    create_response = client.post(
        "/api/v1/opportunities",
        json=_opportunity_payload(owner_user, family),
        headers=owner_headers,
    )
    assert create_response.status_code == 201
    opportunity = create_response.json()["data"]
    assert opportunity["family"]["primary_contact_name"] == "Aarav Sharma"
    assert "primary_contact_name" not in _opportunity_payload(owner_user, family)

    pipeline_response = client.get("/api/v1/opportunities/pipeline", headers=owner_headers)
    assert pipeline_response.status_code == 200
    assert pipeline_response.json()["data"]["PACKAGE_SENT"][0]["id"] == opportunity["id"]

    followup_response = client.post(
        "/api/v1/followups",
        json={
            "opportunity_id": opportunity["id"],
            "assigned_to_user_id": str(owner_user.id),
            "followup_type": "WHATSAPP",
            "due_date": str(date.today() - timedelta(days=1)),
            "notes": "Follow up after package.",
        },
        headers=owner_headers,
    )
    assert followup_response.status_code == 201

    missed_response = client.get("/api/v1/followups?status=MISSED", headers=owner_headers)
    assert missed_response.status_code == 200
    assert missed_response.json()["meta"]["total"] == 1

    update_response = client.put(
        f"/api/v1/opportunities/{opportunity['id']}",
        json={"current_stage": "INTERESTED", "stage_change_notes": "Customer replied."},
        headers=owner_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["current_stage"] == "INTERESTED"

    history_response = client.get(
        f"/api/v1/opportunities/{opportunity['id']}/history", headers=owner_headers
    )
    assert history_response.status_code == 200
    assert history_response.json()["data"][0]["to_stage"] == "INTERESTED"

    metrics_response = client.get("/api/v1/opportunities/metrics", headers=owner_headers)
    assert metrics_response.status_code == 200
    assert metrics_response.json()["data"]["missed_followups"] == 1


def test_lost_stage_requires_lost_reason(
    client: TestClient,
    db: Session,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch is not None
    family = _create_family(db, owner_user.organization, owner_user.branch)
    payload = _opportunity_payload(owner_user, family)
    payload["current_stage"] = "LOST"

    response = client.post("/api/v1/opportunities", json=payload, headers=owner_headers)
    assert response.status_code == 422

    reason = db.query(LostReason).filter(LostReason.name == "Stopped Responding").one()
    payload["lost_reason_id"] = str(reason.id)
    response = client.post("/api/v1/opportunities", json=payload, headers=owner_headers)
    assert response.status_code == 201


def test_booked_opportunity_is_read_only(
    client: TestClient,
    db: Session,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch is not None
    family = _create_family(db, owner_user.organization, owner_user.branch)
    create_response = client.post(
        "/api/v1/opportunities",
        json=_opportunity_payload(owner_user, family),
        headers=owner_headers,
    )
    opportunity_id = create_response.json()["data"]["id"]

    booked_response = client.put(
        f"/api/v1/opportunities/{opportunity_id}",
        json={"current_stage": "BOOKED"},
        headers=owner_headers,
    )
    assert booked_response.status_code == 200

    edit_response = client.put(
        f"/api/v1/opportunities/{opportunity_id}",
        json={"probability": 90},
        headers=owner_headers,
    )
    assert edit_response.status_code == 409

    delete_response = client.delete(
        f"/api/v1/opportunities/{opportunity_id}", headers=owner_headers
    )
    assert delete_response.status_code == 409


def test_sales_can_write_and_photographer_is_read_only(
    client: TestClient,
    db: Session,
) -> None:
    organization = Organization(name="Sales Studio", code="SLS", is_active=True)
    branch = Branch(
        organization=organization,
        name="Sales Branch",
        code="SLS-BR",
        city="Delhi",
        is_active=True,
    )
    db.add(organization)
    db.commit()
    sales_user = _create_user(db, organization, branch, "Sales Executive")
    photographer = _create_user(db, organization, branch, "Photographer")
    family = _create_family(db, organization, branch)

    create_response = client.post(
        "/api/v1/opportunities",
        json=_opportunity_payload(sales_user, family),
        headers=_headers(sales_user),
    )
    assert create_response.status_code == 201

    delete_response = client.delete(
        f"/api/v1/opportunities/{create_response.json()['data']['id']}",
        headers=_headers(sales_user),
    )
    assert delete_response.status_code == 403

    read_response = client.get("/api/v1/opportunities", headers=_headers(photographer))
    assert read_response.status_code == 200

    write_response = client.post(
        "/api/v1/opportunities",
        json=_opportunity_payload(photographer, family),
        headers=_headers(photographer),
    )
    assert write_response.status_code == 403
