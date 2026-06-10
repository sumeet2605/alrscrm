from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.bookings.enums import BookingItemStatus, BookingStatus, ShootStatus
from app.bookings.models import (
    Booking,
    BookingItem,
    BookingItemAddon,
    PhotographerAssignment,
    ShootSchedule,
)
from app.bookings.repositories import BookingRepository
from app.bookings.schemas import (
    BookingCreate,
    BookingUpdate,
    PackageAddonCreate,
    PackageAddonUpdate,
    PackageCreate,
    PackageUpdate,
    PhotographerAssignmentCreate,
    ShootScheduleCreate,
    ShootScheduleUpdate,
)
from app.families.models import Family
from app.identity.models import Branch, User
from app.identity.policies import AuthorizationContext
from app.sales.enums import OpportunityStage
from app.sales.models import Opportunity
from app.shared.exceptions.application import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event


def _scope_filters(
    context: AuthorizationContext, branch_id: UUID | None = None
) -> tuple[UUID | None, UUID | None]:
    if context.is_platform_admin:
        return None, branch_id
    scoped_branch_id = branch_id
    if context.is_branch_scoped:
        if branch_id is not None and branch_id != context.branch_id:
            raise ForbiddenError("Booking branch is outside the caller scope")
        scoped_branch_id = context.branch_id
    return context.organization_id, scoped_branch_id


def _ensure_branch_scope(db: Session, context: AuthorizationContext, branch_id: UUID) -> Branch:
    branch = db.get(Branch, branch_id)
    if branch is None or not branch.is_active:
        raise NotFoundError("Branch not found")
    if not context.is_platform_admin:
        if branch.organization_id != context.organization_id:
            raise ForbiddenError("Branch is outside the caller scope")
        if context.is_branch_scoped and branch.id != context.branch_id:
            raise ForbiddenError("Branch is outside the caller scope")
    return branch


def _ensure_family_scope(db: Session, context: AuthorizationContext, family_id: UUID) -> Family:
    family = db.get(Family, family_id)
    if family is None or family.deleted_at is not None:
        raise NotFoundError("Family not found")
    if not context.is_platform_admin:
        if family.organization_id != context.organization_id:
            raise ForbiddenError("Family is outside the caller scope")
        if context.is_branch_scoped and family.branch_id != context.branch_id:
            raise ForbiddenError("Family is outside the caller scope")
    return family


def _ensure_user_scope(db: Session, context: AuthorizationContext, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise NotFoundError("User not found")
    if not context.is_platform_admin:
        if user.organization_id != context.organization_id:
            raise ForbiddenError("User is outside the caller scope")
        if context.is_branch_scoped and user.branch_id != context.branch_id:
            raise ForbiddenError("User is outside the caller scope")
    return user


def _ensure_booking_scope(context: AuthorizationContext, booking: Booking) -> None:
    if context.is_platform_admin:
        return
    if booking.organization_id != context.organization_id:
        raise ForbiddenError("Booking is outside the caller scope")
    if context.is_branch_scoped and booking.branch_id != context.branch_id:
        raise ForbiddenError("Booking is outside the caller scope")


def _ensure_booking_editable(booking: Booking) -> None:
    if booking.booking_status == BookingStatus.CANCELLED.value:
        raise ConflictError("Cancelled bookings are read-only")


def _booking_event(previous_status: str | None, next_status: str) -> tuple[str, str]:
    if previous_status is None:
        return "booking.created", "BookingCreated"
    if next_status == BookingStatus.CONFIRMED.value:
        return "booking.confirmed", "BookingConfirmed"
    if next_status == BookingStatus.CANCELLED.value:
        return "booking.cancelled", "BookingCancelled"
    if next_status == BookingStatus.COMPLETED.value:
        return "booking.completed", "BookingCompleted"
    return "booking.updated", "BookingUpdated"


def _generate_booking_number(db: Session, branch_code: str) -> str:
    year = datetime.now(UTC).year
    count = db.query(Booking).count() + 1
    return f"BK-{branch_code}-{year}-{count:06d}"


def _build_booking_items(
    repository: BookingRepository,
    payload_items,
    branch_id: UUID,
    organization_id: UUID,
) -> tuple[list[BookingItem], Decimal]:
    items: list[BookingItem] = []
    booking_total = Decimal("0")
    for item_payload in payload_items:
        package = repository.get_package(item_payload.package_id)
        if package is None or not package.is_active:
            raise NotFoundError("Package not found")
        if package.branch_id != branch_id or package.organization_id != organization_id:
            raise ValidationError("Package must belong to the booking branch")
        price = package.price
        final_amount = price - item_payload.discount
        if final_amount < 0:
            raise ValidationError("Booking item discount cannot exceed package price")
        booking_item = BookingItem(
            package_id=package.id,
            service_type=item_payload.service_type.value,
            price=price,
            discount=item_payload.discount,
            final_amount=final_amount,
            status=BookingItemStatus.PENDING.value,
        )
        for addon_payload in item_payload.addons:
            addon = repository.get_addon(addon_payload.addon_id)
            if addon is None or not addon.is_active:
                raise NotFoundError("Addon not found")
            if addon.branch_id != branch_id or addon.organization_id != organization_id:
                raise ValidationError("Addon must belong to the booking branch")
            booking_item.addons.append(
                BookingItemAddon(addon_id=addon.id, price=addon.price, created_at=datetime.now(UTC))
            )
            final_amount += addon.price
        booking_item.final_amount = final_amount
        booking_total += final_amount
        items.append(booking_item)
    if not items:
        raise ValidationError("Booking must contain at least one item")
    return items, booking_total


def _apply_totals(booking: Booking, total_amount: Decimal, advance_received: Decimal) -> None:
    if advance_received > total_amount:
        raise ValidationError("Advance received cannot exceed booking total")
    booking.total_amount = total_amount
    booking.advance_received = advance_received
    booking.balance_amount = total_amount - advance_received


def list_bookings(db: Session, context: AuthorizationContext, **kwargs) -> PageResult:
    organization_id, branch_id = _scope_filters(context, kwargs.pop("branch_id", None))
    elevated_roles = ("Owner", "Branch Manager", "Sales Executive", "Super Admin")
    if "Photographer" in context.role_names and not any(
        role in context.role_names for role in elevated_roles
    ):
        kwargs["photographer_id"] = context.user_id
    return BookingRepository(db).list_bookings(
        organization_id=organization_id, branch_id=branch_id, **kwargs
    )


def get_booking(db: Session, booking_id: UUID, context: AuthorizationContext) -> Booking:
    booking = BookingRepository(db).get_booking(booking_id)
    if booking is None:
        raise NotFoundError("Booking not found")
    _ensure_booking_scope(context, booking)
    return booking


def create_booking(db: Session, payload: BookingCreate, context: AuthorizationContext) -> Booking:
    repository = BookingRepository(db)
    family = _ensure_family_scope(db, context, payload.family_id)
    branch = _ensure_branch_scope(db, context, payload.branch_id)
    opportunity = db.get(Opportunity, payload.opportunity_id)
    if opportunity is None or opportunity.deleted_at is not None:
        raise NotFoundError("Opportunity not found")
    if opportunity.current_stage != OpportunityStage.BOOKED.value:
        raise ValidationError("Booking can be created only from a BOOKED opportunity")
    if opportunity.family_id != family.id:
        raise ValidationError("Booking opportunity must belong to the selected family")
    if family.branch_id != payload.branch_id or branch.organization_id != payload.organization_id:
        raise ValidationError("Booking branch must match family and organization")
    if (
        opportunity.branch_id != payload.branch_id
        or opportunity.organization_id != payload.organization_id
    ):
        raise ValidationError("Booking opportunity must match branch and organization")
    items, total_amount = _build_booking_items(
        repository, payload.items, branch.id, branch.organization_id
    )
    booking = Booking(
        organization_id=payload.organization_id,
        branch_id=payload.branch_id,
        family_id=payload.family_id,
        opportunity_id=payload.opportunity_id,
        booking_number=_generate_booking_number(db, branch.code),
        booking_status=payload.booking_status.value,
        booking_date=payload.booking_date,
        notes=payload.notes,
    )
    _apply_totals(booking, total_amount, payload.advance_received)
    booking.items = items
    repository.create_booking(booking)
    try:
        db.flush()
        event_name, domain_event = _booking_event(None, booking.booking_status)
        record_audit_event(
            db,
            event_name,
            context.user_id,
            "Booking",
            booking.id,
            metadata={"domain_event": domain_event},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValidationError("Booking could not be created") from exc
    return get_booking(db, booking.id, context)


def update_booking(
    db: Session, booking_id: UUID, payload: BookingUpdate, context: AuthorizationContext
) -> Booking:
    repository = BookingRepository(db)
    booking = get_booking(db, booking_id, context)
    _ensure_booking_editable(booking)
    previous_status = booking.booking_status
    repository.update_booking(booking, payload)
    total_amount = booking.total_amount
    if payload.items is not None:
        items, total_amount = _build_booking_items(
            repository, payload.items, booking.branch_id, booking.organization_id
        )
        repository.replace_items(booking, items)
    _apply_totals(
        booking,
        total_amount,
        payload.advance_received
        if payload.advance_received is not None
        else booking.advance_received,
    )
    event_name, domain_event = _booking_event(previous_status, booking.booking_status)
    record_audit_event(
        db,
        event_name,
        context.user_id,
        "Booking",
        booking.id,
        metadata={"domain_event": domain_event},
    )
    db.commit()
    return get_booking(db, booking.id, context)


def delete_booking(db: Session, booking_id: UUID, context: AuthorizationContext) -> None:
    booking = get_booking(db, booking_id, context)
    _ensure_booking_editable(booking)
    BookingRepository(db).soft_delete_booking(booking)
    record_audit_event(db, "booking.deleted", context.user_id, "Booking", booking.id)
    db.commit()


def list_packages(db: Session, context: AuthorizationContext, branch_id: UUID | None = None):
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    return BookingRepository(db).list_packages(organization_id, scoped_branch_id)


def create_package(db: Session, payload: PackageCreate, context: AuthorizationContext):
    branch = _ensure_branch_scope(db, context, payload.branch_id)
    if payload.organization_id != branch.organization_id:
        raise ValidationError("Package organization must match branch")
    item = BookingRepository(db).create_package(payload)
    db.commit()
    db.refresh(item)
    return item


def update_package(
    db: Session, package_id: UUID, payload: PackageUpdate, context: AuthorizationContext
):
    repository = BookingRepository(db)
    item = repository.get_package(package_id)
    if item is None:
        raise NotFoundError("Package not found")
    _ensure_branch_scope(db, context, item.branch_id)
    repository.update_package(item, payload)
    db.commit()
    db.refresh(item)
    return item


def get_package(db: Session, package_id: UUID, context: AuthorizationContext):
    item = BookingRepository(db).get_package(package_id)
    if item is None:
        raise NotFoundError("Package not found")
    _ensure_branch_scope(db, context, item.branch_id)
    return item


def list_addons(db: Session, context: AuthorizationContext, branch_id: UUID | None = None):
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    return BookingRepository(db).list_addons(organization_id, scoped_branch_id)


def create_addon(db: Session, payload: PackageAddonCreate, context: AuthorizationContext):
    branch = _ensure_branch_scope(db, context, payload.branch_id)
    if payload.organization_id != branch.organization_id:
        raise ValidationError("Addon organization must match branch")
    item = BookingRepository(db).create_addon(payload)
    db.commit()
    db.refresh(item)
    return item


def update_addon(
    db: Session, addon_id: UUID, payload: PackageAddonUpdate, context: AuthorizationContext
):
    repository = BookingRepository(db)
    item = repository.get_addon(addon_id)
    if item is None:
        raise NotFoundError("Addon not found")
    _ensure_branch_scope(db, context, item.branch_id)
    repository.update_addon(item, payload)
    db.commit()
    db.refresh(item)
    return item


def get_addon(db: Session, addon_id: UUID, context: AuthorizationContext):
    item = BookingRepository(db).get_addon(addon_id)
    if item is None:
        raise NotFoundError("Addon not found")
    _ensure_branch_scope(db, context, item.branch_id)
    return item


def create_schedule(db: Session, payload: ShootScheduleCreate, context: AuthorizationContext):
    booking = get_booking(db, payload.booking_id, context)
    _ensure_booking_editable(booking)
    if payload.scheduled_end <= payload.scheduled_start:
        raise ValidationError("Schedule end must be after start")
    if not any(item.id == payload.booking_item_id for item in booking.items):
        raise ValidationError("Schedule booking item must belong to booking")
    schedule = ShootSchedule(**payload.model_dump())
    BookingRepository(db).create_schedule(schedule)
    record_audit_event(
        db,
        "shoot.scheduled",
        context.user_id,
        "ShootSchedule",
        schedule.id,
        metadata={"domain_event": "ShootScheduled"},
    )
    db.commit()
    db.refresh(schedule)
    return schedule


def list_schedules(db: Session, context: AuthorizationContext, **kwargs) -> PageResult:
    organization_id, branch_id = _scope_filters(context, kwargs.pop("branch_id", None))
    if "Photographer" in context.role_names and not any(
        role in context.role_names for role in ("Owner", "Branch Manager", "Super Admin")
    ):
        kwargs["photographer_id"] = context.user_id
    return BookingRepository(db).list_schedules(
        organization_id=organization_id, branch_id=branch_id, **kwargs
    )


def get_schedule(db: Session, schedule_id: UUID, context: AuthorizationContext):
    schedule = BookingRepository(db).get_schedule(schedule_id)
    if schedule is None:
        raise NotFoundError("Schedule not found")
    _ensure_booking_scope(context, schedule.booking)
    return schedule


def update_schedule(
    db: Session, schedule_id: UUID, payload: ShootScheduleUpdate, context: AuthorizationContext
):
    repository = BookingRepository(db)
    schedule = get_schedule(db, schedule_id, context)
    _ensure_booking_editable(schedule.booking)
    previous_status = schedule.shoot_status
    repository.update_schedule(schedule, payload)
    if schedule.scheduled_end <= schedule.scheduled_start:
        raise ValidationError("Schedule end must be after start")
    domain_event = "ShootRescheduled"
    event_name = "shoot.rescheduled"
    if (
        schedule.shoot_status == ShootStatus.COMPLETED.value
        and previous_status != schedule.shoot_status
    ):
        domain_event = "ShootCompleted"
        event_name = "shoot.completed"
    record_audit_event(
        db,
        event_name,
        context.user_id,
        "ShootSchedule",
        schedule.id,
        metadata={"domain_event": domain_event},
    )
    db.commit()
    db.refresh(schedule)
    return schedule


def create_assignment(
    db: Session, payload: PhotographerAssignmentCreate, context: AuthorizationContext
):
    repository = BookingRepository(db)
    schedule = get_schedule(db, payload.shoot_schedule_id, context)
    _ensure_booking_editable(schedule.booking)
    _ensure_user_scope(db, context, payload.user_id)
    assignment = PhotographerAssignment(
        shoot_schedule_id=payload.shoot_schedule_id,
        user_id=payload.user_id,
        role=payload.role.value,
        assigned_at=datetime.now(UTC),
    )
    repository.create_assignment(assignment)
    record_audit_event(
        db,
        "photographer.assigned",
        context.user_id,
        "PhotographerAssignment",
        assignment.id,
        metadata={"domain_event": "PhotographerAssigned"},
    )
    db.commit()
    db.refresh(assignment)
    return assignment


def list_assignments(
    db: Session, context: AuthorizationContext, photographer_id: UUID | None = None
):
    organization_id, branch_id = _scope_filters(context)
    if "Photographer" in context.role_names and not any(
        role in context.role_names for role in ("Owner", "Branch Manager", "Super Admin")
    ):
        photographer_id = context.user_id
    return BookingRepository(db).list_assignments(organization_id, branch_id, photographer_id)


def delete_assignment(db: Session, assignment_id: UUID, context: AuthorizationContext) -> None:
    repository = BookingRepository(db)
    assignment = repository.get_assignment(assignment_id)
    if assignment is None:
        raise NotFoundError("Assignment not found")
    _ensure_booking_scope(context, assignment.shoot_schedule.booking)
    _ensure_booking_editable(assignment.shoot_schedule.booking)
    repository.delete_assignment(assignment)
    db.commit()


def get_metrics(db: Session, context: AuthorizationContext):
    organization_id, branch_id = _scope_filters(context)
    return BookingRepository(db).metrics(organization_id, branch_id)
