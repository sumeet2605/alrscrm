from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.families.models import Family
from app.identity.models import Branch, User
from app.identity.policies import AuthorizationContext
from app.sales.enums import FollowUpStatus, OpportunityStage
from app.sales.models import FollowUp, LostReason, Opportunity
from app.sales.repositories import SalesRepository
from app.sales.schemas import (
    FollowUpCreate,
    FollowUpUpdate,
    OpportunityCreate,
    OpportunityNoteCreate,
    OpportunityUpdate,
)
from app.sales.validators import ensure_lost_reason_for_stage, ensure_opportunity_editable
from app.shared.exceptions.application import ForbiddenError, NotFoundError, ValidationError
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event


def _scope_filters(
    context: AuthorizationContext,
    branch_id: UUID | None = None,
) -> tuple[UUID | None, UUID | None]:
    if context.is_platform_admin:
        return None, branch_id
    scoped_branch_id = branch_id
    if context.is_branch_scoped:
        if branch_id is not None and branch_id != context.branch_id:
            raise ForbiddenError("Opportunity branch is outside the caller scope")
        scoped_branch_id = context.branch_id
    return context.organization_id, scoped_branch_id


def _ensure_branch_scope(db: Session, context: AuthorizationContext, branch_id: UUID) -> Branch:
    branch = db.get(Branch, branch_id)
    if branch is None or not branch.is_active:
        raise NotFoundError("Branch not found")
    if not context.is_platform_admin:
        if branch.organization_id != context.organization_id:
            raise ForbiddenError("Opportunity branch is outside the caller scope")
        if context.is_branch_scoped and branch.id != context.branch_id:
            raise ForbiddenError("Opportunity branch is outside the caller scope")
    return branch


def _ensure_user_scope(db: Session, context: AuthorizationContext, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise NotFoundError("Assigned user not found")
    if not context.is_platform_admin:
        if user.organization_id != context.organization_id:
            raise ForbiddenError("Assigned user is outside the caller scope")
        if context.is_branch_scoped and user.branch_id != context.branch_id:
            raise ForbiddenError("Assigned user is outside the caller scope")
    return user


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


def _ensure_lost_reason(db: Session, lost_reason_id: UUID | None) -> LostReason | None:
    if lost_reason_id is None:
        return None
    lost_reason = db.get(LostReason, lost_reason_id)
    if lost_reason is None or not lost_reason.is_active:
        raise NotFoundError("Lost reason not found")
    return lost_reason


def _ensure_opportunity_scope(context: AuthorizationContext, opportunity: Opportunity) -> None:
    if context.is_platform_admin:
        return
    if opportunity.organization_id != context.organization_id:
        raise ForbiddenError("Opportunity is outside the caller scope")
    if context.is_branch_scoped and opportunity.branch_id != context.branch_id:
        raise ForbiddenError("Opportunity is outside the caller scope")


def _ensure_family_branch_consistency(family: Family, branch_id: UUID) -> None:
    if family.branch_id != branch_id:
        raise ValidationError("Opportunity branch must match the referenced family branch")


def list_opportunities(
    db: Session,
    context: AuthorizationContext,
    *,
    page: int = 1,
    page_size: int = 50,
    branch_id: UUID | None = None,
    stage: str | None = None,
    assigned_to_user_id: UUID | None = None,
    opportunity_type: str | None = None,
    lost_reason_id: UUID | None = None,
    search: str | None = None,
) -> PageResult:
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    return SalesRepository(db).list_opportunities(
        page=page,
        page_size=page_size,
        organization_id=organization_id,
        branch_id=scoped_branch_id,
        stage=stage,
        assigned_to_user_id=assigned_to_user_id,
        opportunity_type=opportunity_type,
        lost_reason_id=lost_reason_id,
        search=search,
    )


def get_opportunity(
    db: Session, opportunity_id: UUID, context: AuthorizationContext
) -> Opportunity:
    opportunity = SalesRepository(db).get_opportunity(opportunity_id)
    if opportunity is None:
        raise NotFoundError("Opportunity not found")
    _ensure_opportunity_scope(context, opportunity)
    return opportunity


def create_opportunity(
    db: Session, payload: OpportunityCreate, context: AuthorizationContext
) -> Opportunity:
    family = _ensure_family_scope(db, context, payload.family_id)
    _ensure_family_branch_consistency(family, payload.branch_id)
    branch = _ensure_branch_scope(db, context, payload.branch_id)
    _ensure_user_scope(db, context, payload.assigned_to_user_id)
    _ensure_lost_reason(db, payload.lost_reason_id)
    if payload.organization_id != branch.organization_id:
        raise ValidationError("Opportunity organization must match the selected branch")
    if payload.organization_id != family.organization_id:
        raise ValidationError("Opportunity organization must match the referenced family")
    ensure_lost_reason_for_stage(payload.current_stage.value, payload.lost_reason_id)

    repository = SalesRepository(db)
    opportunity = repository.create_opportunity(payload)
    try:
        db.flush()
        repository.add_stage_history(
            opportunity,
            from_stage=None,
            to_stage=opportunity.current_stage,
            changed_by_user_id=context.user_id,
            notes="Opportunity created",
        )
        record_audit_event(
            db,
            "opportunity.created",
            context.user_id,
            "Opportunity",
            opportunity.id,
            metadata={"event": "OpportunityCreated"},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValidationError("Opportunity could not be created") from exc
    return get_opportunity(db, opportunity.id, context)


def update_opportunity(
    db: Session,
    opportunity_id: UUID,
    payload: OpportunityUpdate,
    context: AuthorizationContext,
) -> Opportunity:
    repository = SalesRepository(db)
    opportunity = get_opportunity(db, opportunity_id, context)
    ensure_opportunity_editable(opportunity.current_stage)

    next_branch_id = payload.branch_id or opportunity.branch_id
    next_family_id = payload.family_id or opportunity.family_id
    next_stage = payload.current_stage.value if payload.current_stage else opportunity.current_stage
    next_lost_reason_id = (
        payload.lost_reason_id
        if "lost_reason_id" in payload.model_fields_set
        else opportunity.lost_reason_id
    )
    family = _ensure_family_scope(db, context, next_family_id)
    _ensure_family_branch_consistency(family, next_branch_id)
    branch = _ensure_branch_scope(db, context, next_branch_id)
    if branch.organization_id != family.organization_id:
        raise ValidationError("Opportunity organization must match the referenced family")
    if payload.assigned_to_user_id is not None:
        _ensure_user_scope(db, context, payload.assigned_to_user_id)
    _ensure_lost_reason(db, next_lost_reason_id)
    ensure_lost_reason_for_stage(next_stage, next_lost_reason_id)

    previous_stage = opportunity.current_stage
    repository.update_opportunity(opportunity, payload)
    opportunity.organization_id = family.organization_id
    if previous_stage != opportunity.current_stage:
        repository.add_stage_history(
            opportunity,
            from_stage=previous_stage,
            to_stage=opportunity.current_stage,
            changed_by_user_id=context.user_id,
            notes=payload.stage_change_notes,
        )
    event_name = _stage_event(previous_stage, opportunity.current_stage)
    record_audit_event(
        db,
        event_name,
        context.user_id,
        "Opportunity",
        opportunity.id,
        metadata={
            "from_stage": previous_stage,
            "to_stage": opportunity.current_stage,
            "domain_event": _domain_event_name(previous_stage, opportunity.current_stage),
        },
    )
    db.commit()
    return get_opportunity(db, opportunity.id, context)


def delete_opportunity(db: Session, opportunity_id: UUID, context: AuthorizationContext) -> None:
    opportunity = get_opportunity(db, opportunity_id, context)
    ensure_opportunity_editable(opportunity.current_stage)
    SalesRepository(db).soft_delete_opportunity(opportunity)
    record_audit_event(db, "opportunity.deleted", context.user_id, "Opportunity", opportunity.id)
    db.commit()


def get_pipeline(db: Session, context: AuthorizationContext) -> dict[str, list[Opportunity]]:
    result = list_opportunities(db, context, page=1, page_size=100)
    grouped = {stage.value: [] for stage in OpportunityStage}
    for item in result.items:
        grouped[item.current_stage].append(item)
    return grouped


def create_followup(
    db: Session, payload: FollowUpCreate, context: AuthorizationContext
) -> FollowUp:
    opportunity = get_opportunity(db, payload.opportunity_id, context)
    ensure_opportunity_editable(opportunity.current_stage)
    _ensure_user_scope(db, context, payload.assigned_to_user_id)
    if payload.status == FollowUpStatus.COMPLETED and payload.completed_at is None:
        payload = payload.model_copy(update={"completed_at": datetime.now(UTC)})
    followup = SalesRepository(db).create_followup(payload)
    db.flush()
    record_audit_event(
        db,
        "followup.created",
        context.user_id,
        "FollowUp",
        followup.id,
        metadata={"domain_event": "FollowUpCreated", "opportunity_id": str(opportunity.id)},
    )
    db.commit()
    db.refresh(followup)
    return followup


def list_followups(
    db: Session,
    context: AuthorizationContext,
    *,
    page: int = 1,
    page_size: int = 50,
    branch_id: UUID | None = None,
    assigned_to_user_id: UUID | None = None,
    status: str | None = None,
    due_from=None,
    due_to=None,
) -> PageResult:
    repository = SalesRepository(db)
    if repository.mark_overdue_followups_missed():
        db.commit()
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    return repository.list_followups(
        page=page,
        page_size=page_size,
        organization_id=organization_id,
        branch_id=scoped_branch_id,
        assigned_to_user_id=assigned_to_user_id,
        status=status,
        due_from=due_from,
        due_to=due_to,
    )


def update_followup(
    db: Session, followup_id: UUID, payload: FollowUpUpdate, context: AuthorizationContext
) -> FollowUp:
    repository = SalesRepository(db)
    followup = repository.get_followup(followup_id)
    if followup is None:
        raise NotFoundError("Follow-up not found")
    _ensure_opportunity_scope(context, followup.opportunity)
    ensure_opportunity_editable(followup.opportunity.current_stage)
    if payload.assigned_to_user_id is not None:
        _ensure_user_scope(db, context, payload.assigned_to_user_id)
    previous_status = followup.status
    if payload.status == FollowUpStatus.COMPLETED and payload.completed_at is None:
        payload = payload.model_copy(update={"completed_at": datetime.now(UTC)})
    repository.update_followup(followup, payload)
    event = "followup.updated"
    domain_event = None
    if previous_status != followup.status:
        if followup.status == FollowUpStatus.COMPLETED.value:
            event = "followup.completed"
            domain_event = "FollowUpCompleted"
        elif followup.status == FollowUpStatus.MISSED.value:
            event = "followup.missed"
            domain_event = "FollowUpMissed"
    record_audit_event(
        db,
        event,
        context.user_id,
        "FollowUp",
        followup.id,
        metadata={"domain_event": domain_event} if domain_event else {},
    )
    db.commit()
    db.refresh(followup)
    return followup


def create_note(
    db: Session,
    opportunity_id: UUID,
    payload: OpportunityNoteCreate,
    context: AuthorizationContext,
):
    opportunity = get_opportunity(db, opportunity_id, context)
    ensure_opportunity_editable(opportunity.current_stage)
    note = SalesRepository(db).create_note(opportunity, context.user_id, payload.note)
    record_audit_event(
        db, "opportunity.note_created", context.user_id, "Opportunity", opportunity.id
    )
    db.commit()
    db.refresh(note)
    return note


def list_notes(db: Session, opportunity_id: UUID, context: AuthorizationContext):
    opportunity = get_opportunity(db, opportunity_id, context)
    return SalesRepository(db).list_notes(opportunity.id)


def list_history(db: Session, opportunity_id: UUID, context: AuthorizationContext):
    opportunity = get_opportunity(db, opportunity_id, context)
    return SalesRepository(db).list_history(opportunity.id)


def list_lost_reasons(db: Session) -> list[LostReason]:
    return SalesRepository(db).list_lost_reasons()


def get_metrics(db: Session, context: AuthorizationContext):
    repository = SalesRepository(db)
    if repository.mark_overdue_followups_missed():
        db.commit()
    organization_id, branch_id = _scope_filters(context)
    return repository.aggregate_counts(organization_id, branch_id)


def _stage_event(previous_stage: str, next_stage: str) -> str:
    if next_stage == OpportunityStage.BOOKED.value:
        return "opportunity.booked"
    if next_stage == OpportunityStage.LOST.value:
        return "opportunity.lost"
    if previous_stage != next_stage:
        return "opportunity.stage_changed"
    return "opportunity.updated"


def _domain_event_name(previous_stage: str, next_stage: str) -> str:
    if next_stage == OpportunityStage.BOOKED.value:
        return "OpportunityBooked"
    if next_stage == OpportunityStage.LOST.value:
        return "OpportunityLost"
    if previous_stage != next_stage:
        return "OpportunityStageChanged"
    return "OpportunityUpdated"
