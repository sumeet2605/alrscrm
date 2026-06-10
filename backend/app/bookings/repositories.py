from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.bookings.enums import ShootStatus
from app.bookings.models import (
    Booking,
    BookingItem,
    BookingItemAddon,
    Package,
    PackageAddon,
    PhotographerAssignment,
    ShootSchedule,
)
from app.bookings.schemas import (
    BookingUpdate,
    PackageAddonCreate,
    PackageAddonUpdate,
    PackageCreate,
    PackageUpdate,
    ShootScheduleUpdate,
)
from app.families.models import Family
from app.sales.models import Opportunity
from app.shared.pagination import PageResult, paginate_query


class BookingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def booking_options(self):
        return (
            joinedload(Booking.family),
            joinedload(Booking.opportunity),
            selectinload(Booking.items).joinedload(BookingItem.package),
            selectinload(Booking.items)
            .selectinload(BookingItem.addons)
            .joinedload(BookingItemAddon.addon),
            selectinload(Booking.items).selectinload(BookingItem.schedules),
        )

    def get_booking(self, booking_id: UUID, include_deleted: bool = False) -> Booking | None:
        query = (
            self.db.query(Booking).options(*self.booking_options()).filter(Booking.id == booking_id)
        )
        if not include_deleted:
            query = query.filter(Booking.deleted_at.is_(None))
        return query.one_or_none()

    def list_bookings(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        search: str | None = None,
        booking_status: str | None = None,
        service_type: str | None = None,
        photographer_id: UUID | None = None,
        booking_from: date | None = None,
        booking_to: date | None = None,
    ) -> PageResult:
        query = (
            self.db.query(Booking)
            .join(Family, Booking.family_id == Family.id)
            .options(*self.booking_options())
            .filter(Booking.deleted_at.is_(None))
        )
        if organization_id is not None:
            query = query.filter(Booking.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Booking.branch_id == branch_id)
        if booking_status is not None:
            query = query.filter(Booking.booking_status == booking_status)
        if service_type is not None:
            query = query.join(BookingItem).filter(BookingItem.service_type == service_type)
        if photographer_id is not None:
            query = (
                query.join(ShootSchedule, ShootSchedule.booking_id == Booking.id)
                .join(PhotographerAssignment)
                .filter(PhotographerAssignment.user_id == photographer_id)
            )
        if booking_from is not None:
            query = query.filter(Booking.booking_date >= booking_from)
        if booking_to is not None:
            query = query.filter(Booking.booking_date <= booking_to)
        if search:
            needle = f"%{search.strip().lower()}%"
            query = query.outerjoin(Opportunity, Booking.opportunity_id == Opportunity.id).filter(
                or_(
                    func.lower(Booking.booking_number).like(needle),
                    func.lower(Family.primary_contact_name).like(needle),
                    func.lower(Family.primary_contact_phone).like(needle),
                    func.lower(Family.family_code).like(needle),
                    func.lower(Opportunity.opportunity_type).like(needle),
                )
            )
        return paginate_query(query.distinct().order_by(Booking.created_at.desc()), page, page_size)

    def create_booking(self, booking: Booking) -> Booking:
        self.db.add(booking)
        return booking

    def replace_items(self, booking: Booking, items: list[BookingItem]) -> None:
        booking.items.clear()
        booking.items.extend(items)

    def update_booking(self, booking: Booking, payload: BookingUpdate) -> None:
        for field, value in payload.model_dump(exclude_unset=True, exclude={"items"}).items():
            setattr(booking, field, value)

    def soft_delete_booking(self, booking: Booking) -> None:
        booking.deleted_at = datetime.now(UTC)

    def list_packages(
        self, organization_id: UUID | None, branch_id: UUID | None, active_only: bool = False
    ) -> list[Package]:
        query = self.db.query(Package)
        if organization_id is not None:
            query = query.filter(Package.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Package.branch_id == branch_id)
        if active_only:
            query = query.filter(Package.is_active.is_(True))
        return query.order_by(Package.name).all()

    def get_package(self, package_id: UUID) -> Package | None:
        return self.db.get(Package, package_id)

    def package_name_exists(
        self, branch_id: UUID, service_type: str, name: str, exclude_id: UUID | None = None
    ) -> bool:
        query = self.db.query(Package.id).filter(
            Package.branch_id == branch_id,
            Package.service_type == service_type,
            func.lower(Package.name) == name.strip().lower(),
        )
        if exclude_id is not None:
            query = query.filter(Package.id != exclude_id)
        return query.first() is not None

    def create_package(self, payload: PackageCreate) -> Package:
        item = Package(**payload.model_dump())
        self.db.add(item)
        return item

    def update_package(self, item: Package, payload: PackageUpdate) -> None:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)

    def list_addons(
        self, organization_id: UUID | None, branch_id: UUID | None, active_only: bool = False
    ) -> list[PackageAddon]:
        query = self.db.query(PackageAddon)
        if organization_id is not None:
            query = query.filter(PackageAddon.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(PackageAddon.branch_id == branch_id)
        if active_only:
            query = query.filter(PackageAddon.is_active.is_(True))
        return query.order_by(PackageAddon.name).all()

    def get_addon(self, addon_id: UUID) -> PackageAddon | None:
        return self.db.get(PackageAddon, addon_id)

    def addon_name_exists(self, branch_id: UUID, name: str, exclude_id: UUID | None = None) -> bool:
        query = self.db.query(PackageAddon.id).filter(
            PackageAddon.branch_id == branch_id,
            func.lower(PackageAddon.name) == name.strip().lower(),
        )
        if exclude_id is not None:
            query = query.filter(PackageAddon.id != exclude_id)
        return query.first() is not None

    def create_addon(self, payload: PackageAddonCreate) -> PackageAddon:
        item = PackageAddon(**payload.model_dump())
        self.db.add(item)
        return item

    def update_addon(self, item: PackageAddon, payload: PackageAddonUpdate) -> None:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)

    def get_schedule(self, schedule_id: UUID) -> ShootSchedule | None:
        return (
            self.db.query(ShootSchedule)
            .options(
                joinedload(ShootSchedule.booking),
                joinedload(ShootSchedule.booking_item),
                selectinload(ShootSchedule.assignments).joinedload(PhotographerAssignment.user),
            )
            .filter(ShootSchedule.id == schedule_id)
            .one_or_none()
        )

    def list_schedules(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        shoot_status: str | None = None,
        photographer_id: UUID | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
    ) -> PageResult:
        query = (
            self.db.query(ShootSchedule)
            .join(Booking, ShootSchedule.booking_id == Booking.id)
            .options(
                joinedload(ShootSchedule.booking).joinedload(Booking.family),
                selectinload(ShootSchedule.assignments).joinedload(PhotographerAssignment.user),
            )
            .filter(Booking.deleted_at.is_(None))
        )
        if organization_id is not None:
            query = query.filter(Booking.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Booking.branch_id == branch_id)
        if shoot_status is not None:
            query = query.filter(ShootSchedule.shoot_status == shoot_status)
        if photographer_id is not None:
            query = query.join(PhotographerAssignment).filter(
                PhotographerAssignment.user_id == photographer_id
            )
        if scheduled_from is not None:
            query = query.filter(ShootSchedule.scheduled_start >= scheduled_from)
        if scheduled_to is not None:
            query = query.filter(ShootSchedule.scheduled_start <= scheduled_to)
        return paginate_query(
            query.distinct().order_by(ShootSchedule.scheduled_start), page, page_size
        )

    def create_schedule(self, schedule: ShootSchedule) -> ShootSchedule:
        self.db.add(schedule)
        return schedule

    def update_schedule(self, schedule: ShootSchedule, payload: ShootScheduleUpdate) -> None:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(schedule, field, value)

    def create_assignment(self, assignment: PhotographerAssignment) -> PhotographerAssignment:
        self.db.add(assignment)
        return assignment

    def get_assignment(self, assignment_id: UUID) -> PhotographerAssignment | None:
        return (
            self.db.query(PhotographerAssignment)
            .options(
                joinedload(PhotographerAssignment.shoot_schedule).joinedload(ShootSchedule.booking)
            )
            .filter(PhotographerAssignment.id == assignment_id)
            .one_or_none()
        )

    def list_assignments(
        self,
        organization_id: UUID | None,
        branch_id: UUID | None,
        photographer_id: UUID | None = None,
    ) -> list[PhotographerAssignment]:
        query = (
            self.db.query(PhotographerAssignment)
            .join(ShootSchedule)
            .join(Booking)
            .options(
                joinedload(PhotographerAssignment.user),
                joinedload(PhotographerAssignment.shoot_schedule),
            )
            .filter(Booking.deleted_at.is_(None))
        )
        if organization_id is not None:
            query = query.filter(Booking.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Booking.branch_id == branch_id)
        if photographer_id is not None:
            query = query.filter(PhotographerAssignment.user_id == photographer_id)
        return query.order_by(PhotographerAssignment.assigned_at.desc()).all()

    def delete_assignment(self, assignment: PhotographerAssignment) -> None:
        self.db.delete(assignment)

    def metrics(
        self, organization_id: UUID | None, branch_id: UUID | None
    ) -> dict[str, int | float]:
        booking_query = self.db.query(Booking).filter(Booking.deleted_at.is_(None))
        schedule_query = (
            self.db.query(ShootSchedule).join(Booking).filter(Booking.deleted_at.is_(None))
        )
        if organization_id is not None:
            booking_query = booking_query.filter(Booking.organization_id == organization_id)
            schedule_query = schedule_query.filter(Booking.organization_id == organization_id)
        if branch_id is not None:
            booking_query = booking_query.filter(Booking.branch_id == branch_id)
            schedule_query = schedule_query.filter(Booking.branch_id == branch_id)
        total = booking_query.count()
        revenue = booking_query.with_entities(func.sum(Booking.total_amount)).scalar() or 0
        assigned = (
            self.db.query(func.count(PhotographerAssignment.id))
            .join(ShootSchedule)
            .join(Booking)
            .filter(Booking.deleted_at.is_(None))
        )
        if organization_id is not None:
            assigned = assigned.filter(Booking.organization_id == organization_id)
        if branch_id is not None:
            assigned = assigned.filter(Booking.branch_id == branch_id)
        total_schedules = schedule_query.count()
        return {
            "total_bookings": total,
            "upcoming_shoots": schedule_query.filter(
                ShootSchedule.scheduled_start >= datetime.now(UTC),
                ShootSchedule.shoot_status.in_(
                    [ShootStatus.SCHEDULED.value, ShootStatus.RESCHEDULED.value]
                ),
            ).count(),
            "completed_shoots": schedule_query.filter(
                ShootSchedule.shoot_status == ShootStatus.COMPLETED.value
            ).count(),
            "cancelled_shoots": schedule_query.filter(
                ShootSchedule.shoot_status == ShootStatus.CANCELLED.value
            ).count(),
            "revenue_booked": float(revenue),
            "average_booking_value": float(revenue / total) if total else 0,
            "photographer_utilization": round((assigned.scalar() / total_schedules) * 100, 2)
            if total_schedules
            else 0,
        }
