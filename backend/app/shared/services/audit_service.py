from uuid import UUID

from sqlalchemy.orm import Session

from app.shared.models.audit_log import AuditLog


def record_audit_event(
    db: Session,
    action: str,
    actor_user_id: UUID | None = None,
    target_type: str | None = None,
    target_id: UUID | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata_json=metadata or {},
        )
    )
