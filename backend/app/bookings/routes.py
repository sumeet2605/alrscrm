from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.bookings.enums import BookingStatus, ServiceType, ShootStatus
from app.bookings.schemas import (
    BookingCreate,
    BookingMetricsRead,
    BookingRead,
    BookingUpdate,
    PackageAddonCreate,
    PackageAddonRead,
    PackageAddonUpdate,
    PackageCreate,
    PackageRead,
    PackageUpdate,
    PhotographerAssignmentCreate,
    PhotographerAssignmentRead,
    ShootScheduleCreate,
    ShootScheduleRead,
    ShootScheduleUpdate,
)
from app.bookings.services import booking_service
from app.core.database import get_db

bookings_router = APIRouter(prefix="/bookings", tags=["Bookings"])
packages_router = APIRouter(prefix="/packages", tags=["Packages"])
addons_router = APIRouter(prefix="/addons", tags=["Package Addons"])
schedules_router = APIRouter(prefix="/schedules", tags=["Schedules"])
assignments_router = APIRouter(prefix="/assignments", tags=["Assignments"])


def _booking(item) -> dict:
    return BookingRead.model_validate(item).model_dump(mode="json")


def _schedule(item) -> dict:
    return ShootScheduleRead.model_validate(item).model_dump(mode="json")


@bookings_router.get("", response_model=APIResponse)
def list_bookings(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None),
    booking_status: BookingStatus | None = Query(default=None),
    service_type: ServiceType | None = Query(default=None),
    photographer_id: UUID | None = Query(default=None),
    booking_from: date | None = Query(default=None),
    booking_to: date | None = Query(default=None),
    branch_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:read")),
):
    result = booking_service.list_bookings(
        db,
        context,
        page=page,
        page_size=page_size,
        search=search,
        booking_status=booking_status.value if booking_status else None,
        service_type=service_type.value if service_type else None,
        photographer_id=photographer_id,
        booking_from=booking_from,
        booking_to=booking_to,
        branch_id=branch_id,
    )
    return api_response(
        "Bookings retrieved",
        [_booking(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@bookings_router.get("/metrics", response_model=APIResponse)
def get_booking_metrics(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:read")),
):
    metrics = BookingMetricsRead(**booking_service.get_metrics(db, context))
    return api_response("Booking metrics retrieved", metrics.model_dump(mode="json"))


@bookings_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:write")),
):
    item = booking_service.create_booking(db, payload, context)
    return api_response("Booking created", _booking(item))


@bookings_router.get("/{booking_id}", response_model=APIResponse)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:read")),
):
    item = booking_service.get_booking(db, booking_id, context)
    return api_response("Booking retrieved", _booking(item))


@bookings_router.put("/{booking_id}", response_model=APIResponse)
def update_booking(
    booking_id: UUID,
    payload: BookingUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:write")),
):
    item = booking_service.update_booking(db, booking_id, payload, context)
    return api_response("Booking updated", _booking(item))


@bookings_router.delete("/{booking_id}", response_model=APIResponse)
def delete_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:delete")),
):
    booking_service.delete_booking(db, booking_id, context)
    return api_response("Booking deleted", {})


@packages_router.get("", response_model=APIResponse)
def list_packages(
    branch_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:packages:read")),
):
    items = booking_service.list_packages(db, context, branch_id)
    return api_response(
        "Packages retrieved",
        [PackageRead.model_validate(item).model_dump(mode="json") for item in items],
    )


@packages_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_package(
    payload: PackageCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:packages:write")),
):
    item = booking_service.create_package(db, payload, context)
    return api_response("Package created", PackageRead.model_validate(item).model_dump(mode="json"))


@packages_router.get("/{package_id}", response_model=APIResponse)
def get_package(
    package_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:packages:read")),
):
    item = booking_service.get_package(db, package_id, context)
    return api_response(
        "Package retrieved", PackageRead.model_validate(item).model_dump(mode="json")
    )


@packages_router.put("/{package_id}", response_model=APIResponse)
def update_package(
    package_id: UUID,
    payload: PackageUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:packages:write")),
):
    item = booking_service.update_package(db, package_id, payload, context)
    return api_response("Package updated", PackageRead.model_validate(item).model_dump(mode="json"))


@addons_router.get("", response_model=APIResponse)
def list_addons(
    branch_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:addons:read")),
):
    items = booking_service.list_addons(db, context, branch_id)
    return api_response(
        "Addons retrieved",
        [PackageAddonRead.model_validate(item).model_dump(mode="json") for item in items],
    )


@addons_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_addon(
    payload: PackageAddonCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:addons:write")),
):
    item = booking_service.create_addon(db, payload, context)
    return api_response(
        "Addon created", PackageAddonRead.model_validate(item).model_dump(mode="json")
    )


@addons_router.put("/{addon_id}", response_model=APIResponse)
def update_addon(
    addon_id: UUID,
    payload: PackageAddonUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:addons:write")),
):
    item = booking_service.update_addon(db, addon_id, payload, context)
    return api_response(
        "Addon updated", PackageAddonRead.model_validate(item).model_dump(mode="json")
    )


@schedules_router.get("", response_model=APIResponse)
def list_schedules(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    shoot_status: ShootStatus | None = Query(default=None),
    photographer_id: UUID | None = Query(default=None),
    scheduled_from: datetime | None = Query(default=None),
    scheduled_to: datetime | None = Query(default=None),
    branch_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:schedules:read")),
):
    result = booking_service.list_schedules(
        db,
        context,
        page=page,
        page_size=page_size,
        shoot_status=shoot_status.value if shoot_status else None,
        photographer_id=photographer_id,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        branch_id=branch_id,
    )
    return api_response(
        "Schedules retrieved",
        [_schedule(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@schedules_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_schedule(
    payload: ShootScheduleCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:schedules:write")),
):
    item = booking_service.create_schedule(db, payload, context)
    return api_response("Schedule created", _schedule(item))


@schedules_router.get("/{schedule_id}", response_model=APIResponse)
def get_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:schedules:read")),
):
    item = booking_service.get_schedule(db, schedule_id, context)
    return api_response("Schedule retrieved", _schedule(item))


@schedules_router.put("/{schedule_id}", response_model=APIResponse)
def update_schedule(
    schedule_id: UUID,
    payload: ShootScheduleUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:schedules:write")),
):
    item = booking_service.update_schedule(db, schedule_id, payload, context)
    return api_response("Schedule updated", _schedule(item))


@assignments_router.get("", response_model=APIResponse)
def list_assignments(
    photographer_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:assignments:read")),
):
    items = booking_service.list_assignments(db, context, photographer_id)
    return api_response(
        "Assignments retrieved",
        [PhotographerAssignmentRead.model_validate(item).model_dump(mode="json") for item in items],
    )


@assignments_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_assignment(
    payload: PhotographerAssignmentCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:assignments:write")),
):
    item = booking_service.create_assignment(db, payload, context)
    return api_response(
        "Assignment created",
        PhotographerAssignmentRead.model_validate(item).model_dump(mode="json"),
    )


@assignments_router.delete("/{assignment_id}", response_model=APIResponse)
def delete_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("bookings:assignments:write")),
):
    booking_service.delete_assignment(db, assignment_id, context)
    return api_response("Assignment deleted", {})
