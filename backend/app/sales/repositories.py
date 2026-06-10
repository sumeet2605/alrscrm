from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.families.models import Family
from app.sales.enums import FollowUpStatus, OpportunityStage
from app.sales.models import (
    FollowUp,
    LostReason,
    Opportunity,
    OpportunityNote,
    OpportunityStageHistory,
)
from app.sales.schemas import FollowUpCreate, FollowUpUpdate, OpportunityCreate, OpportunityUpdate
from app.shared.pagination import PageResult, paginate_query


class SalesRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def opportunity_options(self):
        return (
            joinedload(Opportunity.family),
            joinedload(Opportunity.assigned_to_user),
            joinedload(Opportunity.lost_reason),
            joinedload(Opportunity.followups).joinedload(FollowUp.assigned_to_user),
            joinedload(Opportunity.opportunity_notes).joinedload(OpportunityNote.created_by_user),
            joinedload(Opportunity.stage_history).joinedload(
                OpportunityStageHistory.changed_by_user
            ),
        )

    def pipeline_options(self):
        return (
            joinedload(Opportunity.family),
            joinedload(Opportunity.assigned_to_user),
            joinedload(Opportunity.lost_reason),
            selectinload(Opportunity.followups).joinedload(FollowUp.assigned_to_user),
            selectinload(Opportunity.opportunity_notes).joinedload(OpportunityNote.created_by_user),
            selectinload(Opportunity.stage_history).joinedload(
                OpportunityStageHistory.changed_by_user
            ),
        )

    def get_opportunity(
        self, opportunity_id: UUID, include_deleted: bool = False
    ) -> Opportunity | None:
        query = (
            self.db.query(Opportunity)
            .options(*self.opportunity_options())
            .filter(Opportunity.id == opportunity_id)
        )
        if not include_deleted:
            query = query.filter(Opportunity.deleted_at.is_(None))
        return query.one_or_none()

    def list_opportunities(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        stage: str | None = None,
        assigned_to_user_id: UUID | None = None,
        opportunity_type: str | None = None,
        lost_reason_id: UUID | None = None,
        search: str | None = None,
    ) -> PageResult:
        query = (
            self.db.query(Opportunity)
            .join(Family, Opportunity.family_id == Family.id)
            .options(*self.opportunity_options())
            .filter(Opportunity.deleted_at.is_(None))
        )
        if organization_id is not None:
            query = query.filter(Opportunity.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Opportunity.branch_id == branch_id)
        if stage is not None:
            query = query.filter(Opportunity.current_stage == stage)
        if assigned_to_user_id is not None:
            query = query.filter(Opportunity.assigned_to_user_id == assigned_to_user_id)
        if opportunity_type is not None:
            query = query.filter(Opportunity.opportunity_type == opportunity_type)
        if lost_reason_id is not None:
            query = query.filter(Opportunity.lost_reason_id == lost_reason_id)
        if search:
            needle = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(Family.primary_contact_name).like(needle),
                    func.lower(Family.primary_contact_phone).like(needle),
                    func.lower(Family.family_code).like(needle),
                    func.lower(Opportunity.opportunity_type).like(needle),
                )
            )
        return paginate_query(query.order_by(Opportunity.created_at.desc()), page, page_size)

    def list_pipeline_opportunities(
        self,
        *,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
    ) -> list[Opportunity]:
        query = (
            self.db.query(Opportunity)
            .options(*self.pipeline_options())
            .filter(Opportunity.deleted_at.is_(None))
        )
        if organization_id is not None:
            query = query.filter(Opportunity.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Opportunity.branch_id == branch_id)
        return query.order_by(Opportunity.current_stage.asc(), Opportunity.created_at.desc()).all()

    def create_opportunity(self, payload: OpportunityCreate) -> Opportunity:
        opportunity = Opportunity(**payload.model_dump())
        self.db.add(opportunity)
        return opportunity

    def update_opportunity(self, opportunity: Opportunity, payload: OpportunityUpdate) -> None:
        data = payload.model_dump(exclude_unset=True, exclude={"stage_change_notes"})
        for field, value in data.items():
            setattr(opportunity, field, value)

    def soft_delete_opportunity(self, opportunity: Opportunity) -> None:
        opportunity.deleted_at = datetime.now(UTC)

    def add_stage_history(
        self,
        opportunity: Opportunity,
        *,
        from_stage: str | None,
        to_stage: str,
        changed_by_user_id: UUID,
        notes: str | None = None,
    ) -> OpportunityStageHistory:
        item = OpportunityStageHistory(
            opportunity=opportunity,
            from_stage=from_stage,
            to_stage=to_stage,
            changed_by_user_id=changed_by_user_id,
            notes=notes,
            created_at=datetime.now(UTC),
        )
        self.db.add(item)
        return item

    def create_followup(self, payload: FollowUpCreate) -> FollowUp:
        followup = FollowUp(**payload.model_dump())
        self.db.add(followup)
        return followup

    def get_followup(self, followup_id: UUID) -> FollowUp | None:
        return (
            self.db.query(FollowUp)
            .options(
                joinedload(FollowUp.opportunity).joinedload(Opportunity.family),
                joinedload(FollowUp.assigned_to_user),
            )
            .filter(FollowUp.id == followup_id)
            .one_or_none()
        )

    def update_followup(self, followup: FollowUp, payload: FollowUpUpdate) -> None:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(followup, field, value)

    def list_followups(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        assigned_to_user_id: UUID | None = None,
        status: str | None = None,
        due_from: date | None = None,
        due_to: date | None = None,
    ) -> PageResult:
        query = (
            self.db.query(FollowUp)
            .join(Opportunity, FollowUp.opportunity_id == Opportunity.id)
            .options(joinedload(FollowUp.assigned_to_user))
            .filter(Opportunity.deleted_at.is_(None))
        )
        if organization_id is not None:
            query = query.filter(Opportunity.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Opportunity.branch_id == branch_id)
        if assigned_to_user_id is not None:
            query = query.filter(FollowUp.assigned_to_user_id == assigned_to_user_id)
        if status is not None:
            query = query.filter(FollowUp.status == status)
        if due_from is not None:
            query = query.filter(FollowUp.due_date >= due_from)
        if due_to is not None:
            query = query.filter(FollowUp.due_date <= due_to)
        return paginate_query(query.order_by(FollowUp.due_date.asc()), page, page_size)

    def create_note(
        self, opportunity: Opportunity, created_by_user_id: UUID, note: str
    ) -> OpportunityNote:
        item = OpportunityNote(
            opportunity=opportunity,
            created_by_user_id=created_by_user_id,
            note=note,
            created_at=datetime.now(UTC),
        )
        self.db.add(item)
        return item

    def list_notes(self, opportunity_id: UUID) -> list[OpportunityNote]:
        return (
            self.db.query(OpportunityNote)
            .options(joinedload(OpportunityNote.created_by_user))
            .filter(OpportunityNote.opportunity_id == opportunity_id)
            .order_by(OpportunityNote.created_at.desc())
            .all()
        )

    def list_history(self, opportunity_id: UUID) -> list[OpportunityStageHistory]:
        return (
            self.db.query(OpportunityStageHistory)
            .options(joinedload(OpportunityStageHistory.changed_by_user))
            .filter(OpportunityStageHistory.opportunity_id == opportunity_id)
            .order_by(OpportunityStageHistory.created_at.desc())
            .all()
        )

    def list_lost_reasons(self) -> list[LostReason]:
        return (
            self.db.query(LostReason)
            .filter(LostReason.is_active.is_(True))
            .order_by(LostReason.name)
            .all()
        )

    def mark_overdue_followups_missed(
        self, organization_id: UUID | None, branch_id: UUID | None
    ) -> list[UUID]:
        if organization_id is None and branch_id is None:
            return []
        today = date.today()
        query = (
            self.db.query(FollowUp)
            .join(Opportunity, FollowUp.opportunity_id == Opportunity.id)
            .filter(FollowUp.status == FollowUpStatus.PENDING.value, FollowUp.due_date < today)
            .filter(Opportunity.deleted_at.is_(None))
        )
        if organization_id is not None:
            query = query.filter(Opportunity.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Opportunity.branch_id == branch_id)
        followup_ids = [item.id for item in query.with_entities(FollowUp.id).all()]
        if followup_ids:
            (
                self.db.query(FollowUp)
                .filter(FollowUp.id.in_(followup_ids))
                .update(
                    {"status": FollowUpStatus.MISSED.value},
                    synchronize_session=False,
                )
            )
        return followup_ids

    def aggregate_counts(
        self, organization_id: UUID | None, branch_id: UUID | None
    ) -> dict[str, int | float]:
        opportunity_query = self.db.query(Opportunity).filter(Opportunity.deleted_at.is_(None))
        followup_query = (
            self.db.query(FollowUp)
            .join(Opportunity)
            .filter(Opportunity.deleted_at.is_(None))
        )
        if organization_id is not None:
            opportunity_query = opportunity_query.filter(
                Opportunity.organization_id == organization_id
            )
            followup_query = followup_query.filter(Opportunity.organization_id == organization_id)
        if branch_id is not None:
            opportunity_query = opportunity_query.filter(Opportunity.branch_id == branch_id)
            followup_query = followup_query.filter(Opportunity.branch_id == branch_id)
        total = opportunity_query.count()
        booked = opportunity_query.filter(
            Opportunity.current_stage == OpportunityStage.BOOKED.value
        ).count()
        lost = opportunity_query.filter(
            Opportunity.current_stage == OpportunityStage.LOST.value
        ).count()
        open_count = opportunity_query.filter(
            Opportunity.current_stage.notin_(
                [OpportunityStage.BOOKED.value, OpportunityStage.LOST.value]
            )
        ).count()
        pending = followup_query.filter(FollowUp.status == FollowUpStatus.PENDING.value).count()
        missed = followup_query.filter(FollowUp.status == FollowUpStatus.MISSED.value).count()
        due_query = followup_query.filter(FollowUp.due_date <= date.today())
        total_due = due_query.count()
        completed_due = due_query.filter(FollowUp.status == FollowUpStatus.COMPLETED.value).count()
        avg_value = (
            opportunity_query.with_entities(func.avg(Opportunity.estimated_value)).scalar() or 0
        )
        return {
            "open_opportunities": open_count,
            "booked_opportunities": booked,
            "lost_opportunities": lost,
            "conversion_rate": round((booked / total) * 100, 2) if total else 0,
            "pending_followups": pending,
            "missed_followups": missed,
            "follow_up_compliance": round((completed_due / total_due) * 100, 2)
            if total_due
            else 100,
            "average_opportunity_value": float(avg_value),
        }
