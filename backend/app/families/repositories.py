from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session, joinedload

from app.families.models import Family, FamilyAddress, FamilyMember, ServiceInterest
from app.families.schemas import FamilyCreate, FamilyUpdate
from app.families.validators import format_family_code, normalize_phone
from app.shared.pagination import PageResult, paginate_query


class FamilyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, family_id: UUID, include_deleted: bool = False) -> Family | None:
        query = (
            self.db.query(Family)
            .options(
                joinedload(Family.members),
                joinedload(Family.address),
                joinedload(Family.service_interests),
            )
            .filter(Family.id == family_id)
        )
        if not include_deleted:
            query = query.filter(Family.deleted_at.is_(None))
        return query.one_or_none()

    def list(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        status: str | None = None,
        source: str | None = None,
        edd_from: date | None = None,
        edd_to: date | None = None,
        search: str | None = None,
    ) -> PageResult:
        query = self.db.query(Family).filter(Family.deleted_at.is_(None))
        if organization_id is not None:
            query = query.filter(Family.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Family.branch_id == branch_id)
        if status is not None:
            query = query.filter(Family.status == status)
        if source is not None:
            query = query.filter(Family.source == source)
        if edd_from is not None:
            query = query.filter(Family.expected_delivery_date >= edd_from)
        if edd_to is not None:
            query = query.filter(Family.expected_delivery_date <= edd_to)
        if search:
            needle = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(Family.primary_contact_name).like(needle),
                    func.lower(Family.primary_contact_phone).like(needle),
                    func.lower(Family.primary_contact_email).like(needle),
                    func.lower(Family.family_code).like(needle),
                    func.lower(Family.partner_name).like(needle),
                )
            )
        query = query.options(
            joinedload(Family.members),
            joinedload(Family.address),
            joinedload(Family.service_interests),
        ).order_by(Family.created_at.desc())
        return paginate_query(query, page, page_size)

    def exists_by_phone(self, phone: str, exclude_family_id: UUID | None = None) -> bool:
        query = self.db.query(Family.id).filter(
            Family.primary_contact_phone == normalize_phone(phone),
            Family.deleted_at.is_(None),
        )
        if exclude_family_id is not None:
            query = query.filter(Family.id != exclude_family_id)
        return query.first() is not None

    def create(self, payload: FamilyCreate, family_code: str) -> Family:
        data = payload.model_dump(exclude={"members", "address", "service_interests"})
        data["family_code"] = family_code
        data["primary_contact_phone"] = normalize_phone(data["primary_contact_phone"])
        if data.get("partner_phone"):
            data["partner_phone"] = normalize_phone(data["partner_phone"])
        family = Family(**data)
        family.members = [FamilyMember(**item.model_dump()) for item in payload.members]
        family.service_interests = [
            ServiceInterest(**item.model_dump()) for item in payload.service_interests
        ]
        if payload.address is not None:
            family.address = FamilyAddress(**payload.address.model_dump())
        self.db.add(family)
        return family

    def replace_nested(self, family: Family, payload: FamilyUpdate) -> None:
        data = payload.model_dump(exclude_unset=True)
        if "members" in data:
            family.members = [FamilyMember(**item) for item in data["members"] or []]
        if "service_interests" in data:
            family.service_interests = [
                ServiceInterest(**item) for item in data["service_interests"] or []
            ]
        if "address" in data:
            if data["address"] is None:
                family.address = None
            elif family.address is None:
                family.address = FamilyAddress(**data["address"])
            else:
                for field, value in data["address"].items():
                    setattr(family.address, field, value)

    def update_scalar_fields(self, family: Family, payload: FamilyUpdate) -> None:
        nested_fields = {"members", "address", "service_interests"}
        data = payload.model_dump(exclude_unset=True, exclude=nested_fields)
        for field, value in data.items():
            if field in {"primary_contact_phone", "partner_phone"} and value:
                value = normalize_phone(value)
            setattr(family, field, value)

    def soft_delete(self, family: Family) -> None:
        family.deleted_at = datetime.now(UTC)

    def next_family_code(self) -> str:
        dialect_name = self.db.bind.dialect.name if self.db.bind is not None else ""
        if dialect_name == "postgresql":
            sequence_value = self.db.execute(text("SELECT nextval('family_code_seq')")).scalar_one()
            return format_family_code(int(sequence_value))
        max_code = self.db.query(func.max(Family.family_code)).scalar()
        if not max_code:
            return format_family_code(1)
        try:
            return format_family_code(int(str(max_code).split("-")[-1]) + 1)
        except ValueError:
            return format_family_code(self.db.query(Family).count() + 1)
