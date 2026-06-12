from datetime import date

from app.bookings.models import Booking, BookingItem, Package
from app.core.security import create_access_token, hash_password
from app.families.models import Family
from app.galleries.enums import GalleryStatus
from app.identity.models import Branch, Organization, Role, User
from app.sales.models import Opportunity
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _create_user(
    db: Session, organization: Organization, branch: Branch, role_name: str, suffix: str
) -> User:
    role = db.query(Role).filter(Role.name == role_name).one()
    user = User(
        organization=organization,
        branch=branch,
        email=f"{role_name.lower().replace(' ', '.')}{suffix}@editing.example.com",
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


def _fixture(db: Session):
    organization = Organization(name="Editing Studio", code="EDT", is_active=True)
    branch = Branch(
        organization=organization,
        name="Editing Branch",
        code="EDT-BR",
        city="Mumbai",
        is_active=True,
    )
    db.add(organization)
    db.commit()
    owner = _create_user(db, organization, branch, "Owner", ".owner")
    photographer = _create_user(db, organization, branch, "Photographer", ".photographer")
    editor = _create_user(db, organization, branch, "Editor", ".editor")
    family = Family(
        organization=organization,
        branch=branch,
        family_code="ED-900001",
        primary_contact_name="Editing Family",
        primary_contact_phone="+91 96666 00001",
        primary_contact_email="editing@example.com",
        city="Mumbai",
        source="INSTAGRAM",
        status="BOOKED",
    )
    opportunity = Opportunity(
        organization_id=organization.id,
        branch_id=branch.id,
        family=family,
        assigned_to_user_id=owner.id,
        opportunity_type="NEWBORN",
        current_stage="BOOKED",
        estimated_value="25000.00",
        probability=100,
    )
    package = Package(
        organization=organization,
        branch=branch,
        name="Editing Package",
        service_type="NEWBORN",
        price="20000.00",
        is_active=True,
    )
    booking = Booking(
        organization=organization,
        branch=branch,
        family=family,
        opportunity=opportunity,
        booking_number="BK-EDT-2026-000001",
        booking_status="CONFIRMED",
        booking_date=date.today(),
        total_amount="20000.00",
        advance_received="5000.00",
        balance_amount="15000.00",
    )
    item = BookingItem(
        booking=booking,
        package=package,
        service_type="NEWBORN",
        price="20000.00",
        discount="0.00",
        final_amount="20000.00",
        status="COMPLETED",
    )
    db.add_all([family, opportunity, package, booking, item])
    db.commit()
    db.refresh(item)
    return organization, branch, owner, photographer, editor, booking, item


def _submitted_gallery(
    client: TestClient, owner: User, photographer: User, booking: Booking, item: BookingItem
):
    create_response = client.post(
        "/api/v1/galleries",
        json={
            "booking_id": str(booking.id),
            "booking_item_id": str(item.id),
            "gallery_name": "Editing Source Gallery",
        },
        headers=_headers(owner),
    )
    assert create_response.status_code == 201
    gallery = create_response.json()["data"]
    photo_ids = []
    for index in range(2):
        upload_response = client.post(
            f"/api/v1/galleries/{gallery['id']}/photos",
            json={
                "file_name": f"photo-{index}.jpg",
                "storage_path": f"gallery/photo-{index}.jpg",
                "file_size": 2048,
                "image_width": 1600,
                "image_height": 1200,
                "sort_order": index + 1,
            },
            headers=_headers(photographer),
        )
        assert upload_response.status_code == 201
        photo_ids.append(upload_response.json()["data"]["id"])
    open_response = client.put(
        f"/api/v1/galleries/{gallery['id']}",
        json={"gallery_status": GalleryStatus.SELECTION_OPEN.value},
        headers=_headers(owner),
    )
    assert open_response.status_code == 200
    token_response = client.post(
        f"/api/v1/galleries/{gallery['id']}/access-token/rotate",
        headers=_headers(owner),
    )
    assert token_response.status_code == 200
    access_token = token_response.json()["data"]["access_token"]
    for photo_id in photo_ids:
        favorite_response = client.post(
            f"/api/v1/galleries/client/{access_token}/favorites",
            json={
                "gallery_photo_id": photo_id,
                "selected_by_name": "Client Parent",
                "selected_by_email": "client@example.com",
            },
        )
        assert favorite_response.status_code == 201
    submit_response = client.post(
        f"/api/v1/galleries/{gallery['id']}/submit-selection",
        headers=_headers(owner),
    )
    assert submit_response.status_code == 200
    return submit_response.json()["data"]


def test_editing_job_auto_created_and_workflow_completes(client: TestClient, db: Session) -> None:
    _, _, owner, photographer, editor, booking, item = _fixture(db)
    _submitted_gallery(client, owner, photographer, booking, item)

    list_response = client.get("/api/v1/editing/jobs", headers=_headers(owner))
    assert list_response.status_code == 200
    job = list_response.json()["data"][0]
    assert job["editing_status"] == "PENDING"
    assert job["priority"] == "NORMAL"
    assert job["selected_photo_count"] == 2
    assert job["completed_photo_count"] == 0

    assign_response = client.post(
        f"/api/v1/editing/jobs/{job['id']}/assign-editor",
        json={"assigned_editor_id": str(editor.id)},
        headers=_headers(owner),
    )
    assert assign_response.status_code == 200
    assert assign_response.json()["data"]["editing_status"] == "ASSIGNED"

    start_response = client.post(
        f"/api/v1/editing/jobs/{job['id']}/start",
        headers=_headers(editor),
    )
    assert start_response.status_code == 200
    assert start_response.json()["data"]["editing_status"] == "IN_PROGRESS"

    premature_review = client.post(
        f"/api/v1/editing/jobs/{job['id']}/submit-review",
        headers=_headers(editor),
    )
    assert premature_review.status_code == 409

    update_response = client.put(
        f"/api/v1/editing/jobs/{job['id']}",
        json={"completed_photo_count": 2},
        headers=_headers(editor),
    )
    assert update_response.status_code == 200

    review_response = client.post(
        f"/api/v1/editing/jobs/{job['id']}/submit-review",
        headers=_headers(editor),
    )
    assert review_response.status_code == 200
    assert review_response.json()["data"]["editing_status"] == "READY_FOR_REVIEW"

    editor_approve_response = client.post(
        f"/api/v1/editing/jobs/{job['id']}/approve",
        json={"review_notes": "Looks good"},
        headers=_headers(editor),
    )
    assert editor_approve_response.status_code == 403

    approve_response = client.post(
        f"/api/v1/editing/jobs/{job['id']}/approve",
        json={"review_notes": "Approved"},
        headers=_headers(owner),
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["data"]["editing_status"] == "APPROVED"

    ready_response = client.post(
        f"/api/v1/editing/jobs/{job['id']}/ready-for-delivery",
        headers=_headers(owner),
    )
    assert ready_response.status_code == 200
    assert ready_response.json()["data"]["editing_status"] == "READY_FOR_DELIVERY"

    ready_update_response = client.put(
        f"/api/v1/editing/jobs/{job['id']}",
        json={"notes": "Attempted correction after delivery readiness"},
        headers=_headers(owner),
    )
    assert ready_update_response.status_code == 400

    metrics_response = client.get("/api/v1/editing/metrics", headers=_headers(owner))
    assert metrics_response.status_code == 200
    assert metrics_response.json()["data"]["ready_for_delivery"] == 1

    my_work_response = client.get("/api/v1/editing/my-work", headers=_headers(editor))
    assert my_work_response.status_code == 200


def test_gallery_upgrade_request_is_branch_scoped(client: TestClient, db: Session) -> None:
    organization, _, owner, photographer, _, booking, item = _fixture(db)
    other_branch = Branch(
        organization=organization,
        name="Other Editing Branch",
        code="EDT-OTH",
        city="Pune",
        is_active=True,
    )
    db.add(other_branch)
    db.commit()
    other_manager = _create_user(db, organization, other_branch, "Branch Manager", ".other")
    gallery = _submitted_gallery(client, owner, photographer, booking, item)

    request_response = client.post(
        f"/api/v1/galleries/{gallery['id']}/upgrade-request",
        json={"requested_limit": 5, "price_per_photo": 500},
        headers=_headers(owner),
    )
    assert request_response.status_code == 200
    request_id = request_response.json()["data"]["id"]
    assert request_response.json()["data"]["organization_id"] == str(organization.id)

    approve_response = client.put(
        f"/api/v1/galleries/upgrade-requests/{request_id}/approve",
        headers=_headers(other_manager),
    )
    assert approve_response.status_code == 404


def test_editing_job_access_is_tenant_scoped(client: TestClient, db: Session) -> None:
    _, _, owner, photographer, _, booking, item = _fixture(db)
    _submitted_gallery(client, owner, photographer, booking, item)
    list_response = client.get("/api/v1/editing/jobs", headers=_headers(owner))
    assert list_response.status_code == 200
    job_id = list_response.json()["data"][0]["id"]

    other_organization = Organization(name="Other Editing Studio", code="EDO", is_active=True)
    other_branch = Branch(
        organization=other_organization,
        name="Other Editing Branch",
        code="EDO-BR",
        city="Delhi",
        is_active=True,
    )
    db.add(other_organization)
    db.commit()
    other_owner = _create_user(db, other_organization, other_branch, "Owner", ".other-tenant")

    scoped_response = client.get(f"/api/v1/editing/jobs/{job_id}", headers=_headers(other_owner))
    assert scoped_response.status_code == 403
