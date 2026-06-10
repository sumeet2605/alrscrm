from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.sales.enums import FollowUpStatus, OpportunityStage, OpportunityType
from app.sales.schemas import (
    FollowUpCreate,
    FollowUpRead,
    FollowUpUpdate,
    LostReasonRead,
    OpportunityCreate,
    OpportunityMetricsRead,
    OpportunityNoteCreate,
    OpportunityNoteRead,
    OpportunityRead,
    OpportunityStageHistoryRead,
    OpportunityUpdate,
    PipelineRead,
)
from app.sales.services import sales_service

opportunities_router = APIRouter(prefix="/opportunities", tags=["Opportunities"])
followups_router = APIRouter(prefix="/followups", tags=["Follow Ups"])
lost_reasons_router = APIRouter(prefix="/lost-reasons", tags=["Lost Reasons"])


def _opportunity(item) -> dict:
    return OpportunityRead.model_validate(item).model_dump(mode="json")


def _followup(item) -> dict:
    return FollowUpRead.model_validate(item).model_dump(mode="json")


@opportunities_router.get("", response_model=APIResponse)
def list_opportunities(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None),
    stage: OpportunityStage | None = Query(default=None),
    assigned_to_user_id: UUID | None = Query(default=None),
    opportunity_type: OpportunityType | None = Query(default=None),
    lost_reason_id: UUID | None = Query(default=None),
    branch_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:read")),
):
    result = sales_service.list_opportunities(
        db,
        context,
        page=page,
        page_size=page_size,
        search=search,
        stage=stage.value if stage else None,
        assigned_to_user_id=assigned_to_user_id,
        opportunity_type=opportunity_type.value if opportunity_type else None,
        lost_reason_id=lost_reason_id,
        branch_id=branch_id,
    )
    return api_response(
        "Opportunities retrieved",
        [_opportunity(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@opportunities_router.get("/pipeline", response_model=APIResponse)
def get_pipeline(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:read")),
):
    grouped = sales_service.get_pipeline(db, context)
    data = PipelineRead(
        **{stage: [_opportunity(item) for item in items] for stage, items in grouped.items()}
    ).model_dump(mode="json")
    return api_response("Pipeline retrieved", data)


@opportunities_router.get("/metrics", response_model=APIResponse)
def get_metrics(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:read")),
):
    metrics = OpportunityMetricsRead(**sales_service.get_metrics(db, context))
    return api_response("Sales metrics retrieved", metrics.model_dump(mode="json"))


@opportunities_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_opportunity(
    payload: OpportunityCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:write")),
):
    item = sales_service.create_opportunity(db, payload, context)
    return api_response("Opportunity created", _opportunity(item))


@opportunities_router.get("/{opportunity_id}", response_model=APIResponse)
def get_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:read")),
):
    item = sales_service.get_opportunity(db, opportunity_id, context)
    return api_response("Opportunity retrieved", _opportunity(item))


@opportunities_router.put("/{opportunity_id}", response_model=APIResponse)
def update_opportunity(
    opportunity_id: UUID,
    payload: OpportunityUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:write")),
):
    item = sales_service.update_opportunity(db, opportunity_id, payload, context)
    return api_response("Opportunity updated", _opportunity(item))


@opportunities_router.delete("/{opportunity_id}", response_model=APIResponse)
def delete_opportunity(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:delete")),
):
    sales_service.delete_opportunity(db, opportunity_id, context)
    return api_response("Opportunity deleted", {})


@opportunities_router.post(
    "/{opportunity_id}/notes", status_code=status.HTTP_201_CREATED, response_model=APIResponse
)
def create_note(
    opportunity_id: UUID,
    payload: OpportunityNoteCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:write")),
):
    item = sales_service.create_note(db, opportunity_id, payload, context)
    return api_response(
        "Opportunity note created",
        OpportunityNoteRead.model_validate(item).model_dump(mode="json"),
    )


@opportunities_router.get("/{opportunity_id}/notes", response_model=APIResponse)
def list_notes(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:read")),
):
    items = sales_service.list_notes(db, opportunity_id, context)
    return api_response(
        "Opportunity notes retrieved",
        [OpportunityNoteRead.model_validate(item).model_dump(mode="json") for item in items],
    )


@opportunities_router.get("/{opportunity_id}/history", response_model=APIResponse)
def list_history(
    opportunity_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:opportunities:read")),
):
    items = sales_service.list_history(db, opportunity_id, context)
    return api_response(
        "Opportunity history retrieved",
        [
            OpportunityStageHistoryRead.model_validate(item).model_dump(mode="json")
            for item in items
        ],
    )


@followups_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_followup(
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:followups:write")),
):
    item = sales_service.create_followup(db, payload, context)
    return api_response("Follow-up created", _followup(item))


@followups_router.get("", response_model=APIResponse)
def list_followups(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    branch_id: UUID | None = Query(default=None),
    assigned_to_user_id: UUID | None = Query(default=None),
    status_filter: FollowUpStatus | None = Query(default=None, alias="status"),
    due_from: date | None = Query(default=None),
    due_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:followups:read")),
):
    result = sales_service.list_followups(
        db,
        context,
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        assigned_to_user_id=assigned_to_user_id,
        status=status_filter.value if status_filter else None,
        due_from=due_from,
        due_to=due_to,
    )
    return api_response(
        "Follow-ups retrieved",
        [_followup(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@followups_router.put("/{followup_id}", response_model=APIResponse)
def update_followup(
    followup_id: UUID,
    payload: FollowUpUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:followups:write")),
):
    item = sales_service.update_followup(db, followup_id, payload, context)
    return api_response("Follow-up updated", _followup(item))


@lost_reasons_router.get("", response_model=APIResponse)
def list_lost_reasons(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("sales:lost_reasons:read")),
):
    _ = context
    items = sales_service.list_lost_reasons(db)
    return api_response(
        "Lost reasons retrieved",
        [LostReasonRead.model_validate(item).model_dump(mode="json") for item in items],
    )
