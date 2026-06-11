from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from app.bookings.models import Booking, BookingItem, Package
from app.core.security import create_access_token, hash_password
from app.delivery.models import DeliveryAccessToken, DeliveryJob, DeliveryReopenAttempt
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
        email=f"{role_name.lower().replace(' ', '.')}{suffix}@delivery.example.com",
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
    organization = Organization(name="Delivery Studio", code="DLV", is_active=True)
    branch = Branch(
        organization=organization,
        name="Delivery Branch",
        code="DLV-BR",
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
        family_code="DL-900001",
        primary_contact_name="Delivery Family",
        primary_contact_phone="+91 97777 00001",
        primary_contact_email="delivery@example.com",
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
        name="Delivery Package",
        service_type="NEWBORN",
        price="20000.00",
        is_active=True,
    )
    booking = Booking(
        organization=organization,
        branch=branch,
        family=family,
        opportunity=opportunity,
        booking_number="BK-DLV-2026-000001",
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
            "gallery_name": "Delivery Source Gallery",
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
                "file_name": f"delivery-photo-{index}.jpg",
                "storage_path": f"delivery/photo-{index}.jpg",
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
                "selected_by_email": "client-delivery@example.com",
            },
        )
        assert favorite_response.status_code == 201
    submit_response = client.post(
        f"/api/v1/galleries/{gallery['id']}/submit-selection",
        headers=_headers(owner),
    )
    assert submit_response.status_code == 200


def _ready_delivery_job(client: TestClient, db: Session):
    _, _, owner, photographer, editor, booking, item = _fixture(db)
    _submitted_gallery(client, owner, photographer, booking, item)
    editing_job = client.get("/api/v1/editing/jobs", headers=_headers(owner)).json()["data"][0]
    assign_response = client.post(
        f"/api/v1/editing/jobs/{editing_job['id']}/assign-editor",
        json={"assigned_editor_id": str(editor.id)},
        headers=_headers(owner),
    )
    assert assign_response.status_code == 200
    assert (
        client.post(
            f"/api/v1/editing/jobs/{editing_job['id']}/start",
            headers=_headers(editor),
        ).status_code
        == 200
    )
    assert (
        client.put(
            f"/api/v1/editing/jobs/{editing_job['id']}",
            json={"completed_photo_count": 2},
            headers=_headers(editor),
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/editing/jobs/{editing_job['id']}/submit-review",
            headers=_headers(editor),
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/editing/jobs/{editing_job['id']}/approve",
            json={"review_notes": "Approved"},
            headers=_headers(owner),
        ).status_code
        == 200
    )
    ready_response = client.post(
        f"/api/v1/editing/jobs/{editing_job['id']}/ready-for-delivery",
        headers=_headers(owner),
    )
    assert ready_response.status_code == 200
    delivery_response = client.get("/api/v1/delivery/jobs", headers=_headers(owner))
    assert delivery_response.status_code == 200
    delivery_job = delivery_response.json()["data"][0]
    return owner, editor, delivery_job


def _access_token_from_url(access_url: str) -> str:
    return access_url.rsplit("/", 1)[-1]


def _generate_and_send(client: TestClient, owner: User, delivery_job: dict) -> tuple[dict, str]:
    generate_response = client.post(
        f"/api/v1/delivery/jobs/{delivery_job['id']}/generate-zip",
        headers=_headers(owner),
    )
    assert generate_response.status_code == 200
    send_response = client.post(
        f"/api/v1/delivery/jobs/{delivery_job['id']}/send",
        headers=_headers(owner),
    )
    assert send_response.status_code == 200
    sent_job = send_response.json()["data"]
    assert sent_job["delivery_access_url"]
    return sent_job, _access_token_from_url(sent_job["delivery_access_url"])


def _delivery_session(client: TestClient, token: str, password: str | None = None) -> str:
    payload = {"token": token}
    if password is not None:
        payload["password"] = password
    response = client.post("/api/v1/delivery/public/authenticate", json=payload)
    assert response.status_code == 200
    return response.json()["data"]["session_token"]


def test_ready_for_delivery_creates_delivery_job(client: TestClient, db: Session) -> None:
    owner, _, delivery_job = _ready_delivery_job(client, db)

    assert delivery_job["delivery_status"] == "PENDING"
    assert delivery_job["edited_photo_count"] == 2
    assert delivery_job["download_count"] == 0
    assert delivery_job["max_downloads"] == 10
    assert delivery_job["delivery_link"] is None
    assert delivery_job["password_required"] is False

    metrics_response = client.get("/api/v1/delivery/metrics", headers=_headers(owner))
    assert metrics_response.status_code == 200
    assert metrics_response.json()["data"]["pending_delivery"] == 1


def test_delivery_download_limit_and_audit(client: TestClient, db: Session) -> None:
    owner, _, delivery_job = _ready_delivery_job(client, db)
    update_response = client.put(
        f"/api/v1/delivery/jobs/{delivery_job['id']}",
        json={"max_downloads": 1},
        headers=_headers(owner),
    )
    assert update_response.status_code == 200
    _, token = _generate_and_send(client, owner, delivery_job)

    public_response = client.get(f"/api/v1/delivery/client/{token}")
    assert public_response.status_code == 200
    session_token = _delivery_session(client, token)
    download_response = client.post(
        f"/api/v1/delivery/client/{token}/download",
        headers={"Authorization": f"Bearer {session_token}"},
    )
    assert download_response.status_code == 200
    assert download_response.json()["data"]["download_count"] == 1
    assert download_response.json()["data"]["download_url"]

    blocked_response = client.post(
        f"/api/v1/delivery/client/{token}/download",
        headers={"Authorization": f"Bearer {session_token}"},
    )
    assert blocked_response.status_code == 403

    downloads_response = client.get(
        f"/api/v1/delivery/jobs/{delivery_job['id']}/downloads",
        headers=_headers(owner),
    )
    assert downloads_response.status_code == 200
    assert len(downloads_response.json()["data"]) == 1


def test_delivery_expiry_and_reopen(client: TestClient, db: Session) -> None:
    owner, _, delivery_job = _ready_delivery_job(client, db)
    _, token = _generate_and_send(client, owner, delivery_job)

    job = db.get(DeliveryJob, UUID(delivery_job["id"]))
    assert job is not None
    job.expiry_date = date.today() - timedelta(days=1)
    db.commit()

    expired_response = client.get(f"/api/v1/delivery/client/{token}")
    assert expired_response.status_code == 410

    reopen_response = client.post(
        f"/api/v1/delivery/client/{token}/reopen-request",
        json={
            "requested_by_name": "Client Parent",
            "requested_by_email": "client@example.com",
            "reason": "Need one more download",
        },
    )
    assert reopen_response.status_code == 409


def test_reopen_requires_delivered_state_and_cooldown(client: TestClient, db: Session) -> None:
    owner, _, delivery_job = _ready_delivery_job(client, db)
    _, token = _generate_and_send(client, owner, delivery_job)
    session_token = _delivery_session(client, token)
    assert (
        client.post(
            f"/api/v1/delivery/client/{token}/download",
            headers={"Authorization": f"Bearer {session_token}"},
        ).status_code
        == 200
    )

    payload = {
        "requested_by_name": "Client Parent",
        "requested_by_email": "client@example.com",
        "reason": "Need one more download",
    }
    reopen_response = client.post(f"/api/v1/delivery/client/{token}/reopen-request", json=payload)
    assert reopen_response.status_code == 200
    assert reopen_response.json()["data"]["delivery_status"] == "REOPEN_REQUESTED"
    duplicate_response = client.post(
        f"/api/v1/delivery/client/{token}/reopen-request", json=payload
    )
    assert duplicate_response.status_code == 409

    approve_response = client.post(
        f"/api/v1/delivery/jobs/{delivery_job['id']}/approve-reopen",
        headers=_headers(owner),
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["data"]["delivery_status"] == "REOPENED"
    assert approve_response.json()["data"]["delivery_access_url"]


def test_password_protected_delivery_requires_session(client: TestClient, db: Session) -> None:
    owner, _, delivery_job = _ready_delivery_job(client, db)
    update_response = client.put(
        f"/api/v1/delivery/jobs/{delivery_job['id']}",
        json={"password": "ClientPass123"},
        headers=_headers(owner),
    )
    assert update_response.status_code == 200
    sent_job, token = _generate_and_send(client, owner, delivery_job)
    assert sent_job["password_required"] is True

    assert (
        client.post(
            "/api/v1/delivery/public/authenticate",
            json={"token": token, "password": "WrongPass"},
        ).status_code
        == 401
    )
    session_token = _delivery_session(client, token, "ClientPass123")
    download_response = client.post(
        f"/api/v1/delivery/client/{token}/download",
        headers={"Authorization": f"Bearer {session_token}"},
    )
    assert download_response.status_code == 200


def test_expired_and_revoked_access_tokens_are_rejected(client: TestClient, db: Session) -> None:
    owner, _, delivery_job = _ready_delivery_job(client, db)
    _, token = _generate_and_send(client, owner, delivery_job)
    access_token = (
        db.query(DeliveryAccessToken)
        .filter(
            DeliveryAccessToken.delivery_job_id == UUID(delivery_job["id"]),
            DeliveryAccessToken.revoked_at.is_(None),
        )
        .one()
    )
    access_token.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db.commit()
    assert client.get(f"/api/v1/delivery/client/{token}").status_code == 401

    rotate_response = client.post(
        f"/api/v1/delivery/jobs/{delivery_job['id']}/access-token/rotate",
        headers=_headers(owner),
    )
    assert rotate_response.status_code == 200
    new_token = _access_token_from_url(rotate_response.json()["data"]["delivery_access_url"])
    revoke_response = client.post(
        f"/api/v1/delivery/jobs/{delivery_job['id']}/access-token/revoke",
        headers=_headers(owner),
    )
    assert revoke_response.status_code == 200
    assert client.get(f"/api/v1/delivery/client/{new_token}").status_code == 401


def test_reopen_request_rate_limit(client: TestClient, db: Session) -> None:
    owner, _, delivery_job = _ready_delivery_job(client, db)
    _, token = _generate_and_send(client, owner, delivery_job)
    session_token = _delivery_session(client, token)
    assert (
        client.post(
            f"/api/v1/delivery/client/{token}/download",
            headers={"Authorization": f"Bearer {session_token}"},
        ).status_code
        == 200
    )
    now = datetime.now(UTC)
    for _ in range(5):
        db.add(
            DeliveryReopenAttempt(
                delivery_job_id=UUID(delivery_job["id"]),
                ip_address="testclient",
                attempted_at=now,
            )
        )
    db.commit()
    response = client.post(
        f"/api/v1/delivery/client/{token}/reopen-request",
        json={
            "requested_by_name": "Client Parent",
            "requested_by_email": "client@example.com",
            "reason": "Need one more download",
        },
    )
    assert response.status_code == 403


def test_delivery_lifecycle_status_cannot_be_bypassed(client: TestClient, db: Session) -> None:
    owner, _, delivery_job = _ready_delivery_job(client, db)
    response = client.put(
        f"/api/v1/delivery/jobs/{delivery_job['id']}",
        json={"delivery_status": "SENT", "zip_generation_status": "COMPLETED"},
        headers=_headers(owner),
    )
    assert response.status_code == 422


def test_delivery_access_is_tenant_scoped_and_editor_is_view_only(
    client: TestClient, db: Session
) -> None:
    _, editor, delivery_job = _ready_delivery_job(client, db)

    editor_view = client.get(
        f"/api/v1/delivery/jobs/{delivery_job['id']}", headers=_headers(editor)
    )
    assert editor_view.status_code == 200
    editor_update = client.post(
        f"/api/v1/delivery/jobs/{delivery_job['id']}/send",
        headers=_headers(editor),
    )
    assert editor_update.status_code == 403

    other_branch = Branch(
        organization=editor.organization,
        name="Other Branch",
        code="DLV-OTHER",
        city="Pune",
        is_active=True,
    )
    db.add(other_branch)
    db.commit()
    other_branch_manager = _create_user(
        db, editor.organization, other_branch, "Branch Manager", ".other-branch"
    )
    branch_scoped_response = client.get(
        f"/api/v1/delivery/jobs/{delivery_job['id']}",
        headers=_headers(other_branch_manager),
    )
    assert branch_scoped_response.status_code == 403

    other_organization = Organization(name="Other Delivery Studio", code="DLO", is_active=True)
    other_branch = Branch(
        organization=other_organization,
        name="Other Delivery Branch",
        code="DLO-BR",
        city="Delhi",
        is_active=True,
    )
    db.add(other_organization)
    db.commit()
    other_owner = _create_user(db, other_organization, other_branch, "Owner", ".other-tenant")

    scoped_response = client.get(
        f"/api/v1/delivery/jobs/{delivery_job['id']}",
        headers=_headers(other_owner),
    )
    assert scoped_response.status_code == 403
