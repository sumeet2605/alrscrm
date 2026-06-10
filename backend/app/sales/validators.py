from app.sales.enums import OpportunityStage
from app.shared.exceptions.application import ConflictError, ValidationError


def ensure_lost_reason_for_stage(stage: str, lost_reason_id) -> None:
    if stage == OpportunityStage.LOST.value and lost_reason_id is None:
        raise ValidationError("Lost reason is required when opportunity is lost")


def ensure_opportunity_editable(current_stage: str) -> None:
    if current_stage == OpportunityStage.BOOKED.value:
        raise ConflictError("Booked opportunities are read-only")
