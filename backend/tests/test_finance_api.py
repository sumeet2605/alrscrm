from datetime import date, timedelta

from app.bookings.models import Booking, BookingItem, Package
from app.core.security import create_access_token, hash_password
from app.families.models import Family
from app.identity.models import Branch, Organization, Role, User
from app.sales.models import Opportunity
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _create_user(
    db: Session,
    organization: Organization,
    branch: Branch,
    role_name: str,
    email_prefix: str,
) -> User:
    role = db.query(Role).filter(Role.name == role_name).one()
    user = User(
        organization=organization,
        branch=branch,
        email=f"{email_prefix}@finance.example.com",
        password_hash=hash_password("StrongPass123"),
        first_name=role_name.split()[0],
        last_name="Finance",
        is_active=True,
        roles=[role],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_branch(db: Session, organization: Organization, name: str, code: str) -> Branch:
    branch = Branch(
        organization=organization,
        name=name,
        code=code,
        city="Mumbai",
        is_active=True,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


def _create_family(db: Session, organization: Organization, branch: Branch, code: str) -> Family:
    family = Family(
        organization=organization,
        branch=branch,
        family_code=code,
        primary_contact_name=f"{code} Family",
        primary_contact_phone="+91 98888 10001",
        primary_contact_email=f"{code.lower()}@example.com",
        city="Mumbai",
        source="INSTAGRAM",
        status="BOOKED",
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


def _create_booking(
    db: Session,
    organization: Organization,
    branch: Branch,
    owner: User,
    family: Family,
) -> Booking:
    opportunity = Opportunity(
        organization_id=organization.id,
        branch_id=branch.id,
        family_id=family.id,
        assigned_to_user_id=owner.id,
        opportunity_type="NEWBORN",
        current_stage="BOOKED",
        estimated_value="25000.00",
        probability=100,
    )
    package = Package(
        organization_id=organization.id,
        branch_id=branch.id,
        name=f"Finance Package {branch.code}",
        service_type="NEWBORN",
        price="20000.00",
        is_active=True,
    )
    db.add_all([opportunity, package])
    db.flush()
    booking = Booking(
        organization_id=organization.id,
        branch_id=branch.id,
        family_id=family.id,
        opportunity_id=opportunity.id,
        booking_number=f"BK-{branch.code}",
        booking_status="CONFIRMED",
        total_amount="20000.00",
        advance_received="0.00",
        balance_amount="20000.00",
        booking_date=date.today(),
        items=[
            BookingItem(
                package_id=package.id,
                service_type="NEWBORN",
                price="20000.00",
                discount="0.00",
                final_amount="20000.00",
                status="PENDING",
            )
        ],
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def _fixture(db: Session):
    organization = Organization(name="Finance Studio", code="FIN", is_active=True)
    other_organization = Organization(name="Other Finance Studio", code="OFIN", is_active=True)
    db.add_all([organization, other_organization])
    db.commit()
    branch = _create_branch(db, organization, "Main Finance Branch", "FIN-MAIN")
    other_branch = _create_branch(db, organization, "Second Finance Branch", "FIN-SECOND")
    tenant_branch = _create_branch(db, other_organization, "Tenant Finance Branch", "OFIN-MAIN")
    owner = _create_user(db, organization, branch, "Owner", "owner")
    branch_manager = _create_user(
        db, organization, other_branch, "Branch Manager", "branch.manager"
    )
    other_owner = _create_user(db, other_organization, tenant_branch, "Owner", "other.owner")
    family = _create_family(db, organization, branch, "FIN-900001")
    booking = _create_booking(db, organization, branch, owner, family)
    return organization, branch, owner, branch_manager, other_owner, family, booking


def _invoice_payload(
    organization: Organization,
    branch: Branch,
    family: Family,
    booking: Booking,
) -> dict:
    return {
        "organization_id": str(organization.id),
        "branch_id": str(branch.id),
        "family_id": str(family.id),
        "booking_id": str(booking.id),
        "currency": "INR",
        "due_date": str(date.today() + timedelta(days=15)),
        "seller_legal_name": "Finance Studio Pvt Ltd",
        "seller_gstin": "27ABCDE1234F1Z5",
        "seller_address": "Studio Road, Mumbai",
        "seller_state_code": "27",
        "buyer_billing_name": "Finance Family",
        "buyer_billing_address": "Client Address, Mumbai",
        "buyer_state_code": "27",
        "place_of_supply_state_code": "27",
        "supply_type": "INTRA_STATE",
        "gst_registration_type": "REGULAR",
        "reverse_charge_applicable": False,
        "line_items": [
            {
                "description": "Newborn photography package",
                "quantity": "1",
                "unit_price": "10000.00",
                "discount_amount": "0.00",
                "tax_rate": "18.00",
                "cgst_rate": "9.00",
                "cgst_amount": "900.00",
                "sgst_rate": "9.00",
                "sgst_amount": "900.00",
                "igst_rate": "0.00",
                "igst_amount": "0.00",
                "service_type": "NEWBORN",
                "sac_code": "9983",
            }
        ],
    }


def test_invoice_payment_metrics_lifecycle(client: TestClient, db: Session) -> None:
    organization, branch, owner, _, _, family, booking = _fixture(db)
    settings_response = client.patch(
        "/api/v1/finance/settings",
        json={
            "branch_id": str(branch.id),
            "registration_type": "REGULAR",
            "gstin": "27ABCDE1234F1Z5",
            "legal_name": "Finance Studio Pvt Ltd",
            "billing_state_code": "27",
            "invoice_prefix": "FIN",
        },
        headers=_headers(owner),
    )
    assert settings_response.status_code == 200

    invoice_response = client.post(
        "/api/v1/invoices",
        json=_invoice_payload(organization, branch, family, booking),
        headers=_headers(owner),
    )
    assert invoice_response.status_code == 201
    invoice = invoice_response.json()["data"]
    assert invoice["invoice_number"].startswith("FIN-")
    assert invoice["invoice_status"] == "DRAFT"
    assert invoice["total_amount"] == "11800.00"
    assert invoice["balance_due"] == "11800.00"
    assert invoice["seller_gstin"] == "27ABCDE1234F1Z5"

    issue_response = client.post(
        f"/api/v1/invoices/{invoice['id']}/issue",
        headers=_headers(owner),
    )
    assert issue_response.status_code == 200
    assert issue_response.json()["data"]["invoice_status"] == "ISSUED"

    payment_response = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice["id"],
            "amount": "5000.00",
            "payment_method": "UPI",
            "payment_status": "COMPLETED",
            "transaction_reference": "UPI-123",
        },
        headers=_headers(owner),
    )
    assert payment_response.status_code == 201
    payment = payment_response.json()["data"]
    assert payment["payment_number"].startswith("PAY-")

    invoice_pdf_response = client.get(
        f"/api/v1/invoices/{invoice['id']}/pdf",
        headers=_headers(owner),
    )
    assert invoice_pdf_response.status_code == 200
    assert invoice_pdf_response.headers["content-type"] == "application/pdf"
    assert invoice_pdf_response.content.startswith(b"%PDF")

    receipt_response = client.get(
        f"/api/v1/payments/{payment['id']}/receipt",
        headers=_headers(owner),
    )
    assert receipt_response.status_code == 200
    assert receipt_response.headers["content-type"] == "application/pdf"
    assert receipt_response.content.startswith(b"%PDF")

    invoice_detail_response = client.get(
        f"/api/v1/invoices/{invoice['id']}",
        headers=_headers(owner),
    )
    assert invoice_detail_response.status_code == 200
    invoice_detail = invoice_detail_response.json()["data"]
    assert invoice_detail["invoice_status"] == "PARTIALLY_PAID"
    assert invoice_detail["amount_paid"] == "5000.00"
    assert invoice_detail["balance_due"] == "6800.00"

    metrics_response = client.get("/api/v1/finance/metrics", headers=_headers(owner))
    assert metrics_response.status_code == 200
    metrics = metrics_response.json()["data"]
    assert metrics["paid_amount"] == "5000.00"
    assert metrics["outstanding_amount"] == "6800.00"
    assert metrics["invoices_by_status"]["PARTIALLY_PAID"] == 1
    assert metrics["payments_by_method"]["UPI"] == 1


def test_payment_cannot_exceed_invoice_balance(client: TestClient, db: Session) -> None:
    organization, branch, owner, _, _, family, booking = _fixture(db)
    invoice_response = client.post(
        "/api/v1/invoices",
        json=_invoice_payload(organization, branch, family, booking),
        headers=_headers(owner),
    )
    invoice = invoice_response.json()["data"]
    client.post(f"/api/v1/invoices/{invoice['id']}/issue", headers=_headers(owner))

    response = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice["id"],
            "amount": "20000.00",
            "payment_method": "CASH",
            "payment_status": "COMPLETED",
        },
        headers=_headers(owner),
    )
    assert response.status_code == 409
    assert response.json()["message"] == "Payment amount cannot exceed invoice balance"


def test_finance_access_is_tenant_and_branch_scoped(client: TestClient, db: Session) -> None:
    organization, branch, owner, branch_manager, other_owner, family, booking = _fixture(db)
    invoice_response = client.post(
        "/api/v1/invoices",
        json=_invoice_payload(organization, branch, family, booking),
        headers=_headers(owner),
    )
    invoice = invoice_response.json()["data"]

    tenant_response = client.get(
        f"/api/v1/invoices/{invoice['id']}",
        headers=_headers(other_owner),
    )
    assert tenant_response.status_code == 403

    branch_response = client.get(
        f"/api/v1/invoices/{invoice['id']}",
        headers=_headers(branch_manager),
    )
    assert branch_response.status_code == 403

    branch_list_response = client.get("/api/v1/invoices", headers=_headers(branch_manager))
    assert branch_list_response.status_code == 200
    assert branch_list_response.json()["meta"]["total"] == 0
