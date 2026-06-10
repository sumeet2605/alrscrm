from datetime import UTC, date, datetime, timedelta

from app.core.security import create_access_token, hash_password
from app.families.models import Family
from app.identity.models import Branch, Organization, Role, User
from app.sales.models import Opportunity
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _create_user(db: Session, organization: Organization, branch: Branch, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).one()
    user = User(
        organization=organization,
        branch=branch,
        email=f"{role_name.lower().replace(' ', '.')}@booking.example.com",
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


def _create_family(db: Session, organization: Organization, branch: Branch) -> Family:
    family = Family(
        organization=organization,
        branch=branch,
        family_code="BK-900001",
        primary_contact_name="Booking Family",
        primary_contact_phone="+91 98888 00001",
        primary_contact_email="booking@example.com",
        city="Mumbai",
        source="INSTAGRAM",
        status="BOOKED",
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


def _create_opportunity(
    db: Session, user: User, family: Family, stage: str = "BOOKED"
) -> Opportunity:
    opportunity = Opportunity(
        organization_id=family.organization_id,
        branch_id=family.branch_id,
        family_id=family.id,
        assigned_to_user_id=user.id,
        opportunity_type="NEWBORN",
        current_stage=stage,
        estimated_value="25000.00",
        probability=100,
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


def _fixture(db: Session):
    organization = Organization(name="Booking Studio", code="BKG", is_active=True)
    branch = Branch(
        organization=organization,
        name="Booking Branch",
        code="BKG-BR",
        city="Mumbai",
        is_active=True,
    )
    db.add(organization)
    db.commit()
    owner = _create_user(db, organization, branch, "Owner")
    photographer = _create_user(db, organization, branch, "Photographer")
    sales = _create_user(db, organization, branch, "Sales Executive")
    family = _create_family(db, organization, branch)
    opportunity = _create_opportunity(db, owner, family)
    return organization, branch, owner, photographer, sales, family, opportunity


def test_booking_lifecycle_schedule_assignment_and_metrics(client: TestClient, db: Session) -> None:
    organization, branch, owner, photographer, _, family, opportunity = _fixture(db)
    package_response = client.post(
        "/api/v1/packages",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "name": "Newborn Signature",
            "service_type": "NEWBORN",
            "description": "Studio newborn package",
            "price": "20000.00",
            "is_active": True,
        },
        headers=_headers(owner),
    )
    assert package_response.status_code == 201
    package = package_response.json()["data"]

    addon_response = client.post(
        "/api/v1/addons",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "name": "Album",
            "description": "Printed album",
            "price": "5000.00",
            "is_active": True,
        },
        headers=_headers(owner),
    )
    assert addon_response.status_code == 201
    addon = addon_response.json()["data"]

    booking_response = client.post(
        "/api/v1/bookings",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "family_id": str(family.id),
            "opportunity_id": str(opportunity.id),
            "booking_status": "CONFIRMED",
            "advance_received": "5000.00",
            "booking_date": str(date.today()),
            "notes": "Advance collected outside payments module.",
            "items": [
                {
                    "package_id": package["id"],
                    "service_type": "NEWBORN",
                    "discount": "1000.00",
                    "addons": [{"addon_id": addon["id"]}],
                }
            ],
        },
        headers=_headers(owner),
    )
    assert booking_response.status_code == 201
    booking = booking_response.json()["data"]
    assert booking["total_amount"] == "24000.00"
    assert booking["balance_amount"] == "19000.00"
    assert booking["family"]["primary_contact_name"] == "Booking Family"

    item_id = booking["items"][0]["id"]
    schedule_response = client.post(
        "/api/v1/schedules",
        json={
            "booking_id": booking["id"],
            "booking_item_id": item_id,
            "scheduled_start": (datetime.now(UTC) + timedelta(days=2)).isoformat(),
            "scheduled_end": (datetime.now(UTC) + timedelta(days=2, hours=2)).isoformat(),
            "location": "Studio A",
            "shoot_status": "SCHEDULED",
            "notes": "Keep warmer ready.",
        },
        headers=_headers(owner),
    )
    assert schedule_response.status_code == 201
    schedule = schedule_response.json()["data"]

    assignment_response = client.post(
        "/api/v1/assignments",
        json={
            "shoot_schedule_id": schedule["id"],
            "user_id": str(photographer.id),
            "role": "LEAD_PHOTOGRAPHER",
        },
        headers=_headers(owner),
    )
    assert assignment_response.status_code == 201

    photographer_schedules = client.get("/api/v1/schedules", headers=_headers(photographer))
    assert photographer_schedules.status_code == 200
    assert photographer_schedules.json()["meta"]["total"] == 1

    metrics_response = client.get("/api/v1/bookings/metrics", headers=_headers(owner))
    assert metrics_response.status_code == 200
    assert metrics_response.json()["data"]["total_bookings"] == 1
    assert metrics_response.json()["data"]["revenue_booked"] == 24000.0


def test_booking_requires_booked_opportunity(client: TestClient, db: Session) -> None:
    organization, branch, owner, _, _, family, _ = _fixture(db)
    opportunity = _create_opportunity(db, owner, family, stage="INTERESTED")
    package_response = client.post(
        "/api/v1/packages",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "name": "Maternity Base",
            "service_type": "MATERNITY",
            "price": "10000.00",
        },
        headers=_headers(owner),
    )
    response = client.post(
        "/api/v1/bookings",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "family_id": str(family.id),
            "opportunity_id": str(opportunity.id),
            "booking_date": str(date.today()),
            "items": [
                {
                    "package_id": package_response.json()["data"]["id"],
                    "service_type": "MATERNITY",
                }
            ],
        },
        headers=_headers(owner),
    )
    assert response.status_code == 422


def test_sales_cannot_assign_photographer_and_cancelled_booking_is_read_only(
    client: TestClient, db: Session
) -> None:
    organization, branch, owner, photographer, sales, family, opportunity = _fixture(db)
    package_response = client.post(
        "/api/v1/packages",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "name": "Family Base",
            "service_type": "FAMILY",
            "price": "12000.00",
        },
        headers=_headers(owner),
    )
    booking_response = client.post(
        "/api/v1/bookings",
        json={
            "organization_id": str(organization.id),
            "branch_id": str(branch.id),
            "family_id": str(family.id),
            "opportunity_id": str(opportunity.id),
            "booking_status": "CONFIRMED",
            "booking_date": str(date.today()),
            "items": [
                {
                    "package_id": package_response.json()["data"]["id"],
                    "service_type": "FAMILY",
                }
            ],
        },
        headers=_headers(owner),
    )
    booking = booking_response.json()["data"]
    schedule_response = client.post(
        "/api/v1/schedules",
        json={
            "booking_id": booking["id"],
            "booking_item_id": booking["items"][0]["id"],
            "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
            "scheduled_end": (datetime.now(UTC) + timedelta(days=1, hours=2)).isoformat(),
            "location": "Client Home",
            "shoot_status": "SCHEDULED",
        },
        headers=_headers(owner),
    )
    assignment_response = client.post(
        "/api/v1/assignments",
        json={
            "shoot_schedule_id": schedule_response.json()["data"]["id"],
            "user_id": str(photographer.id),
            "role": "LEAD_PHOTOGRAPHER",
        },
        headers=_headers(sales),
    )
    assert assignment_response.status_code == 403

    cancel_response = client.put(
        f"/api/v1/bookings/{booking['id']}",
        json={"booking_status": "CANCELLED"},
        headers=_headers(owner),
    )
    assert cancel_response.status_code == 200

    edit_response = client.put(
        f"/api/v1/bookings/{booking['id']}",
        json={"notes": "Should not update"},
        headers=_headers(owner),
    )
    assert edit_response.status_code == 409
