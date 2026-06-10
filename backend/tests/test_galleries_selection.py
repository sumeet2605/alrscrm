"""Tests for gallery selection governance: selection limit, submission locking, password and expiry."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.bookings.models import Booking, BookingItem, Package
from app.families.models import Family
from app.galleries.enums import GalleryStatus
from app.galleries.models import GalleryPhoto
from app.galleries.services import gallery_service
from app.identity.models import Branch, Organization
from app.sales.models import Opportunity
from app.shared.exceptions.application import BadRequestError, ForbiddenError, GoneError
from app.shared.exceptions.application import ConflictError


def _fixture_minimal(db: Session):
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
        assigned_to_user_id=uuid4(),
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
        booking_date=datetime.utcnow(),
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
    return organization, branch, booking, item


@pytest.mark.usefixtures("db")
def test_selection_limit_enforced(db: Session):
    org, branch, booking, item = _fixture_minimal(db)
    class Ctx:
        user_id = uuid4()
        is_platform_admin = True
        is_branch_scoped = False
        organization_id = org.id
        branch_id = branch.id

    g = gallery_service.create_gallery(
        db,
        type("P", (), {"booking_id": booking.id, "booking_item_id": item.id, "gallery_name": "G1", "gallery_status": GalleryStatus.SELECTION_OPEN, "password": None, "expires_at": None}),
        Ctx(),
    )
    # add three photos
    p1 = GalleryPhoto(gallery_id=g.id, file_name="a", storage_path="/a", file_size=1, image_width=1, image_height=1, sort_order=1, is_active=True, uploaded_at=datetime.utcnow())
    p2 = GalleryPhoto(gallery_id=g.id, file_name="b", storage_path="/b", file_size=1, image_width=1, image_height=1, sort_order=2, is_active=True, uploaded_at=datetime.utcnow())
    p3 = GalleryPhoto(gallery_id=g.id, file_name="c", storage_path="/c", file_size=1, image_width=1, image_height=1, sort_order=3, is_active=True, uploaded_at=datetime.utcnow())
    db.add_all([p1, p2, p3])
    db.commit()
    # set selection_limit to 2
    g.selection_limit = 2
    db.add(g)
    db.commit()

    payload = type("P", (), {"gallery_photo_id": p1.id, "selected_by_name": "Anon", "selected_by_email": None})
    gallery_service.add_favorite(db, g.id, payload, None)
    payload.gallery_photo_id = p2.id
    gallery_service.add_favorite(db, g.id, payload, None)
    payload.gallery_photo_id = p3.id
    with pytest.raises(BadRequestError):
        gallery_service.add_favorite(db, g.id, payload, None)


@pytest.mark.usefixtures("db")
def test_submission_locks_selection(db: Session):
    org, branch, booking, item = _fixture_minimal(db)
    class Ctx:
        user_id = uuid4()
        is_platform_admin = True
        is_branch_scoped = False
        organization_id = org.id
        branch_id = branch.id

    g = gallery_service.create_gallery(
        db,
        type("P", (), {"booking_id": booking.id, "booking_item_id": item.id, "gallery_name": "G2", "gallery_status": GalleryStatus.SELECTION_OPEN, "password": None, "expires_at": None}),
        Ctx(),
    )
    p = GalleryPhoto(gallery_id=g.id, file_name="a", storage_path="/a", file_size=1, image_width=1, image_height=1, sort_order=1, is_active=True, uploaded_at=datetime.utcnow())
    db.add(p)
    db.commit()

    gallery_service.submit_selection(db, g.id, Ctx())
    payload = type("P", (), {"gallery_photo_id": p.id, "selected_by_name": "X", "selected_by_email": None})
    with pytest.raises(ForbiddenError):
        gallery_service.add_favorite(db, g.id, payload, None)


@pytest.mark.usefixtures("db")
def test_password_and_expiry_behaviour(db: Session):
    org, branch, booking, item = _fixture_minimal(db)
    class Ctx:
        user_id = uuid4()
        is_platform_admin = True
        is_branch_scoped = False
        organization_id = org.id
        branch_id = branch.id

    future = datetime.utcnow() + timedelta(days=1)
    # create gallery with future expiry and test auth
    g = gallery_service.create_gallery(
        db,
        type("P", (), {"booking_id": booking.id, "booking_item_id": item.id, "gallery_name": "G3", "gallery_status": GalleryStatus.SELECTION_OPEN, "password": "secret", "expires_at": future}),
        Ctx(),
    )
    with pytest.raises(ForbiddenError):
        gallery_service.authenticate_public_gallery(db, g.id, "wrong")
    token = gallery_service.authenticate_public_gallery(db, g.id, "secret")
    assert token is not None

    # mark gallery expired and ensure public access is gone
    g.expires_at = datetime.utcnow() - timedelta(days=1)
    db.add(g)
    db.commit()
    with pytest.raises(GoneError):
        gallery_service.get_public_gallery(db, g.id)


@pytest.mark.usefixtures("db")
def test_public_submit_flow(db: Session):
    org, branch, booking, item = _fixture_minimal(db)
    class Ctx:
        user_id = uuid4()
        is_platform_admin = True
        is_branch_scoped = False
        organization_id = org.id
        branch_id = branch.id

    # open gallery without password: public submit should work
    g = gallery_service.create_gallery(
        db,
        type("P", (), {"booking_id": booking.id, "booking_item_id": item.id, "gallery_name": "G4", "gallery_status": GalleryStatus.SELECTION_OPEN, "password": None, "expires_at": None}),
        Ctx(),
    )
    # public submit with no token
    gallery_service.submit_public_selection(db, g.id, None)
    # reopen for next tests
    gallery_service.reopen_selection(db, g.id, Ctx())

    # password-protected gallery: cannot submit without token
    future = datetime.utcnow() + timedelta(days=1)
    # create a new booking item for this gallery to avoid unique constraint
    item2 = BookingItem(
        booking=booking,
        package=booking.items[0].package if getattr(booking, 'items', None) else None,
        service_type="NEWBORN",
        price="20000.00",
        discount="0.00",
        final_amount="20000.00",
        status="COMPLETED",
    )
    db.add(item2)
    db.commit()
    db.refresh(item2)
    gp = gallery_service.create_gallery(
        db,
        type("P", (), {"booking_id": booking.id, "booking_item_id": item2.id, "gallery_name": "G5", "gallery_status": GalleryStatus.SELECTION_OPEN, "password": "secret", "expires_at": future}),
        Ctx(),
    )
    with pytest.raises(ForbiddenError):
        gallery_service.submit_public_selection(db, gp.id, None)
    # authenticate and submit using token
    token = gallery_service.authenticate_public_gallery(db, gp.id, "secret")
    assert token is not None
    gallery_service.submit_public_selection(db, gp.id, token)

    # expiry: new gallery expired cannot be submitted
    # create another booking item for expiry test
    item3 = BookingItem(
        booking=booking,
        package=booking.items[0].package if getattr(booking, 'items', None) else None,
        service_type="NEWBORN",
        price="20000.00",
        discount="0.00",
        final_amount="20000.00",
        status="COMPLETED",
    )
    db.add(item3)
    db.commit()
    db.refresh(item3)
    ge = gallery_service.create_gallery(
        db,
        type("P", (), {"booking_id": booking.id, "booking_item_id": item3.id, "gallery_name": "G6", "gallery_status": GalleryStatus.SELECTION_OPEN, "password": None, "expires_at": datetime.utcnow() - timedelta(days=1)}),
        Ctx(),
    )
    with pytest.raises(GoneError):
        gallery_service.submit_public_selection(db, ge.id, None)

