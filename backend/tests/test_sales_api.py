from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from app.bookings.models import Booking, Package
from app.core.security import create_access_token, hash_password
from app.families.models import Family
from app.finance.models import Invoice
from app.identity.models import Branch, Organization, Role, User
from app.sales.models import FollowUp, LostReason, Opportunity
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def _create_family(
    db: Session, organization: Organization, branch: Branch, suffix: str = "900001"
) -> Family:
    family = Family(
        organization=organization,
        branch=branch,
        family_code=f"ALS-{suffix}",
        primary_contact_name=f"Aarav Sharma {suffix}",
        primary_contact_phone=f"+91 90000 {suffix[-5:]}",
        primary_contact_email=f"aarav{suffix}@example.com",
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


def _create_user(
    db: Session, organization: Organization, branch: Branch, role_name: str, suffix: str = ""
) -> User:
    role = db.query(Role).filter(Role.name == role_name).one()
    user = User(
        organization=organization,
        branch=branch,
        email=f"{role_name.lower().replace(' ', '.')}{suffix}@example.com",
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


def _create_opportunity_row(
    db: Session,
    user: User,
    family: Family,
    *,
    stage: str = "PACKAGE_SENT",
    deleted: bool = False,
    lost_reason_id=None,
) -> Opportunity:
    opportunity = Opportunity(
        organization_id=family.organization_id,
        branch_id=family.branch_id,
        family_id=family.id,
        assigned_to_user_id=user.id,
        opportunity_type="NEWBORN",
        current_stage=stage,
        estimated_value="20000.00",
        probability=35,
        expected_booking_date=date.today() + timedelta(days=10),
        lost_reason_id=lost_reason_id,
        deleted_at=datetime.now(UTC) if deleted else None,
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


def _create_followup_row(
    db: Session,
    opportunity: Opportunity,
    assigned_user: User,
    *,
    due_date: date,
    status: str = "PENDING",
) -> FollowUp:
    followup = FollowUp(
        opportunity_id=opportunity.id,
        assigned_to_user_id=assigned_user.id,
        followup_type="WHATSAPP",
        due_date=due_date,
        status=status,
    )
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup


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
    assert opportunity["family"]["primary_contact_name"] == "Aarav Sharma 900001"
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
    opportunity_id = UUID(create_response.json()["data"]["id"])

    booked_response = client.put(
        f"/api/v1/opportunities/{opportunity_id}",
        json={"current_stage": "BOOKED"},
        headers=owner_headers,
    )
    assert booked_response.status_code == 200
    booking = db.query(Booking).filter(Booking.opportunity_id == opportunity_id).one()
    invoice = db.query(Invoice).filter(Invoice.booking_id == booking.id).one()
    assert booking.items == []
    assert booking.total_amount == 0
    assert invoice.invoice_status == "DRAFT"
    assert invoice.total_amount == 0
    assert invoice.line_items[0].description == "Draft invoice - package pending"

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


def test_booked_opportunity_with_package_creates_booking_and_invoice(
    client: TestClient,
    db: Session,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch is not None
    family = _create_family(db, owner_user.organization, owner_user.branch, "900777")
    package = Package(
        organization_id=owner_user.organization_id,
        branch_id=owner_user.branch_id,
        name="Newborn Signature",
        service_type="NEWBORN",
        price="25000.00",
        is_active=True,
    )
    db.add(package)
    db.commit()
    db.refresh(package)
    payload = _opportunity_payload(owner_user, family)
    payload["package_id"] = str(package.id)
    create_response = client.post(
        "/api/v1/opportunities",
        json=payload,
        headers=owner_headers,
    )
    opportunity_id = UUID(create_response.json()["data"]["id"])

    booked_response = client.put(
        f"/api/v1/opportunities/{opportunity_id}",
        json={"current_stage": "BOOKED"},
        headers=owner_headers,
    )

    assert booked_response.status_code == 200
    booking = db.query(Booking).filter(Booking.opportunity_id == opportunity_id).one()
    assert booking.booking_status == "CONFIRMED"
    assert booking.total_amount == 25000
    assert booking.items[0].package_id == package.id
    invoice = db.query(Invoice).filter(Invoice.booking_id == booking.id).one()
    assert invoice.invoice_status == "DRAFT"
    assert invoice.buyer_billing_name == family.primary_contact_name
    assert invoice.total_amount == 25000
    assert invoice.line_items[0].description == "Newborn Signature"


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


def test_overdue_followup_aging_does_not_cross_tenant(
    client: TestClient,
    db: Session,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch is not None
    own_family = _create_family(db, owner_user.organization, owner_user.branch, "910001")
    own_opportunity = _create_opportunity_row(db, owner_user, own_family)
    own_followup = _create_followup_row(
        db, own_opportunity, owner_user, due_date=date.today() - timedelta(days=1)
    )

    other_organization = Organization(name="Other Tenant", code="OTH", is_active=True)
    other_branch = Branch(
        organization=other_organization,
        name="Other Branch",
        code="OTH-BR",
        city="Pune",
        is_active=True,
    )
    db.add(other_organization)
    db.commit()
    other_user = _create_user(db, other_organization, other_branch, "Owner", ".other")
    other_family = _create_family(db, other_organization, other_branch, "910002")
    other_opportunity = _create_opportunity_row(db, other_user, other_family)
    other_followup = _create_followup_row(
        db, other_opportunity, other_user, due_date=date.today() - timedelta(days=1)
    )

    response = client.get("/api/v1/opportunities/metrics", headers=owner_headers)
    assert response.status_code == 200

    db.refresh(own_followup)
    db.refresh(other_followup)
    assert own_followup.status == "MISSED"
    assert other_followup.status == "PENDING"


def test_overdue_followup_aging_does_not_cross_branch(
    client: TestClient,
    db: Session,
) -> None:
    organization = Organization(name="Branch Scope Studio", code="BSS", is_active=True)
    branch_one = Branch(
        organization=organization,
        name="Bandra",
        code="BSS-BAN",
        city="Mumbai",
        is_active=True,
    )
    branch_two = Branch(
        organization=organization,
        name="Thane",
        code="BSS-THA",
        city="Mumbai",
        is_active=True,
    )
    db.add(organization)
    db.commit()
    branch_manager = _create_user(db, organization, branch_one, "Branch Manager", ".branch")
    branch_two_user = _create_user(db, organization, branch_two, "Sales Executive", ".branch2")

    branch_one_family = _create_family(db, organization, branch_one, "920001")
    branch_one_opportunity = _create_opportunity_row(db, branch_manager, branch_one_family)
    branch_one_followup = _create_followup_row(
        db, branch_one_opportunity, branch_manager, due_date=date.today() - timedelta(days=1)
    )

    branch_two_family = _create_family(db, organization, branch_two, "920002")
    branch_two_opportunity = _create_opportunity_row(db, branch_two_user, branch_two_family)
    branch_two_followup = _create_followup_row(
        db, branch_two_opportunity, branch_two_user, due_date=date.today() - timedelta(days=1)
    )

    response = client.get("/api/v1/opportunities/metrics", headers=_headers(branch_manager))
    assert response.status_code == 200

    db.refresh(branch_one_followup)
    db.refresh(branch_two_followup)
    assert branch_one_followup.status == "MISSED"
    assert branch_two_followup.status == "PENDING"


def test_pipeline_returns_more_than_one_hundred_opportunities(
    client: TestClient,
    db: Session,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch is not None
    for index in range(105):
        suffix = f"93{index:04d}"
        family = _create_family(db, owner_user.organization, owner_user.branch, suffix)
        _create_opportunity_row(db, owner_user, family, stage="NEW")

    response = client.get("/api/v1/opportunities/pipeline", headers=owner_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]["NEW"]) == 105


def test_metrics_exclude_followups_from_deleted_opportunities(
    client: TestClient,
    db: Session,
    owner_user: User,
    owner_headers: dict[str, str],
) -> None:
    assert owner_user.branch is not None
    active_family = _create_family(db, owner_user.organization, owner_user.branch, "940001")
    active_opportunity = _create_opportunity_row(db, owner_user, active_family, stage="BOOKED")
    _create_followup_row(
        db,
        active_opportunity,
        owner_user,
        due_date=date.today(),
        status="COMPLETED",
    )

    deleted_family = _create_family(db, owner_user.organization, owner_user.branch, "940002")
    lost_reason = db.query(LostReason).filter(LostReason.name == "Stopped Responding").one()
    deleted_opportunity = _create_opportunity_row(
        db,
        owner_user,
        deleted_family,
        stage="LOST",
        deleted=True,
        lost_reason_id=lost_reason.id,
    )
    _create_followup_row(
        db,
        deleted_opportunity,
        owner_user,
        due_date=date.today(),
        status="MISSED",
    )

    response = client.get("/api/v1/opportunities/metrics", headers=owner_headers)
    assert response.status_code == 200
    metrics = response.json()["data"]
    assert metrics["booked_opportunities"] == 1
    assert metrics["lost_opportunities"] == 0
    assert metrics["missed_followups"] == 0
    assert metrics["follow_up_compliance"] == 100
    assert metrics["average_opportunity_value"] == 20000.0


def test_sales_database_constraints_for_probability_and_lost_reason(
    db: Session,
    owner_user: User,
) -> None:
    assert owner_user.branch is not None
    family = _create_family(db, owner_user.organization, owner_user.branch, "950001")
    invalid_probability = Opportunity(
        organization_id=owner_user.organization_id,
        branch_id=owner_user.branch_id,
        family_id=family.id,
        assigned_to_user_id=owner_user.id,
        opportunity_type="NEWBORN",
        current_stage="NEW",
        estimated_value="20000.00",
        probability=101,
    )
    db.add(invalid_probability)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    else:
        raise AssertionError("Probability check constraint was not enforced")

    invalid_lost = Opportunity(
        organization_id=owner_user.organization_id,
        branch_id=owner_user.branch_id,
        family_id=family.id,
        assigned_to_user_id=owner_user.id,
        opportunity_type="NEWBORN",
        current_stage="LOST",
        estimated_value="20000.00",
        probability=20,
    )
    db.add(invalid_lost)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    else:
        raise AssertionError("LOST stage check constraint was not enforced")
