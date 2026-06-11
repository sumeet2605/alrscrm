from uuid import UUID

from sqlalchemy.orm import Session

from app.identity.models import User
from app.shared.models.audit_log import AuditLog


def record_audit_event(
    db: Session,
    action: str,
    actor_user_id: UUID | None = None,
    target_type: str | None = None,
    target_id: UUID | None = None,
    metadata: dict | None = None,
    organization_id: UUID | None = None,
    branch_id: UUID | None = None,
) -> None:
    if (organization_id is None or branch_id is None) and actor_user_id is not None:
        actor = db.get(User, actor_user_id)
        if actor is not None:
            organization_id = organization_id or actor.organization_id
            branch_id = branch_id or actor.branch_id
    if metadata:
        organization_id = organization_id or _uuid_from_metadata(metadata, "organization_id")
        branch_id = branch_id or _uuid_from_metadata(metadata, "branch_id")
    db.add(
        AuditLog(
            organization_id=organization_id,
            branch_id=branch_id,
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata_json=metadata or {},
        )
    )


def _uuid_from_metadata(metadata: dict, key: str) -> UUID | None:
    value = metadata.get(key)
    if value is None:
        return None
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None
