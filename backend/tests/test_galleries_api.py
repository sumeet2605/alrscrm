from datetime import date

from app.bookings.models import Booking, BookingItem, Package
from app.core.security import create_access_token, hash_password
from app.families.models import Family
from app.galleries.enums import GalleryStatus
from app.galleries.repositories import GalleryRepository
from app.galleries.schemas import GalleryCreate
from app.galleries.services import gallery_service
from app.identity.models import Branch, Organization, Role, User
from app.identity.policies import AuthorizationContext
from app.sales.models import Opportunity
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _gallery_access_token(client: TestClient, gallery_id: str, owner: User) -> str:
    response = client.post(
        f"/api/v1/galleries/{gallery_id}/access-token/rotate",
        headers=_headers(owner),
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def _create_user(db: Session, organization: Organization, branch: Branch, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).one()
    user = User(
        organization=organization,
        branch=branch,
        email=f"{role_name.lower().replace(' ', '.')}@gallery.example.com",
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
    organization = Organization(name="Gallery Studio", code="GLR", is_active=True)
    branch = Branch(
        organization=organization,
        name="Gallery Branch",
        code="GLR-BR",
        city="Mumbai",
        is_active=True,
    )
    db.add(organization)
    db.commit()
    owner = _create_user(db, organization, branch, "Owner")
    photographer = _create_user(db, organization, branch, "Photographer")
    family = Family(
        organization=organization,
        branch=branch,
        family_code="GL-900001",
        primary_contact_name="Gallery Family",
        primary_contact_phone="+91 97777 00001",
        primary_contact_email="gallery@example.com",
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
        name="Gallery Package",
        service_type="NEWBORN",
        price="20000.00",
        is_active=True,
    )
    booking = Booking(
        organization=organization,
        branch=branch,
        family=family,
        opportunity=opportunity,
        booking_number="BK-GLR-2026-000001",
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
    return organization, branch, owner, photographer, booking, item


def test_gallery_service_and_repository_metrics(db: Session) -> None:
    _, _, owner, _, booking, item = _fixture(db)
    context = AuthorizationContext.from_user(owner)
    gallery = gallery_service.create_gallery(
        db,
        GalleryCreate(
            booking_id=booking.id,
            booking_item_id=item.id,
            gallery_name="Newborn Highlights",
        ),
        context,
    )

    metrics = GalleryRepository(db).metrics(owner.organization_id, owner.branch_id)
    assert gallery.booking_item_id == item.id
    assert metrics["total_galleries"] == 1
    assert metrics["photos_uploaded"] == 0


def test_gallery_api_selection_workflow(client: TestClient, db: Session) -> None:
    _, _, owner, photographer, booking, item = _fixture(db)
    create_response = client.post(
        "/api/v1/galleries",
        json={
            "booking_id": str(booking.id),
            "booking_item_id": str(item.id),
            "gallery_name": "Client Selection",
        },
        headers=_headers(owner),
    )
    assert create_response.status_code == 201
    gallery = create_response.json()["data"]

    upload_response = client.post(
        f"/api/v1/galleries/{gallery['id']}/photos",
        json={
            "file_name": "photo-001.jpg",
            "storage_path": "gallery/photo-001.jpg",
            "thumbnail_path": "gallery/thumb-photo-001.jpg",
            "file_size": 2048,
            "image_width": 1600,
            "image_height": 1200,
        },
        headers=_headers(photographer),
    )
    assert upload_response.status_code == 201
    photo = upload_response.json()["data"]

    open_response = client.put(
        f"/api/v1/galleries/{gallery['id']}",
        json={"gallery_status": GalleryStatus.SELECTION_OPEN.value},
        headers=_headers(owner),
    )
    assert open_response.status_code == 200
    access_token = _gallery_access_token(client, gallery["id"], owner)

    favorite_response = client.post(
        f"/api/v1/galleries/client/{access_token}/favorites",
        json={
            "gallery_photo_id": photo["id"],
            "selected_by_name": "Client Parent",
            "selected_by_email": "client@example.com",
        },
    )
    assert favorite_response.status_code == 201
    uuid_public_response = client.get(f"/api/v1/galleries/{gallery['id']}/public")
    assert uuid_public_response.status_code in {403, 404}

    metrics_response = client.get("/api/v1/galleries/metrics", headers=_headers(owner))
    assert metrics_response.status_code == 200
    assert metrics_response.json()["data"] == {
        "total_galleries": 1,
        "photos_uploaded": 1,
        "selection_open_galleries": 1,
        "selection_closed_galleries": 0,
        "favorite_count": 1,
    }


def test_gallery_multipart_upload_returns_renderable_photo_url(
    client: TestClient, db: Session
) -> None:
    _, _, owner, photographer, booking, item = _fixture(db)
    create_response = client.post(
        "/api/v1/galleries",
        json={
            "booking_id": str(booking.id),
            "booking_item_id": str(item.id),
            "gallery_name": "Upload Gallery",
        },
        headers=_headers(owner),
    )
    gallery = create_response.json()["data"]

    upload_response = client.post(
        f"/api/v1/galleries/{gallery['id']}/photos/upload",
        files={"file": ("photo.jpg", b"fake-image-bytes", "image/jpeg")},
        data={"image_width": "1200", "image_height": "800"},
        headers=_headers(photographer),
    )
    assert upload_response.status_code == 201
    photo = upload_response.json()["data"]
    assert photo["thumbnail_path"].startswith("data:image/jpeg;base64,")

    access_token = _gallery_access_token(client, gallery["id"], owner)
    public_response = client.get(f"/api/v1/galleries/client/{access_token}")
    assert public_response.status_code == 200
    public_photo = public_response.json()["data"]["photos"][0]
    assert public_photo["thumbnail_path"].startswith("data:image/jpeg;base64,")
