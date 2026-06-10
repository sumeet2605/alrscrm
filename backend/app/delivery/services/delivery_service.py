import json
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.delivery.enums import DeliveryStatus, ZipGenerationStatus
from app.delivery.models import DeliveryAudit, DeliveryDownload, DeliveryJob
from app.delivery.repositories import DeliveryRepository
from app.delivery.schemas import DeliveryJobCreate, DeliveryJobUpdate, DeliveryReopenRequest
from app.editing.enums import EditingStatus
from app.editing.models import EditingJob
from app.identity.policies import AuthorizationContext
from app.shared.exceptions.application import (
    ConflictError,
    ForbiddenError,
    GoneError,
    NotFoundError,
)
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event

DEFAULT_MAX_DOWNLOADS = 10
DEFAULT_EXPIRY_DAYS = 90


def _scope_filters(
    context: AuthorizationContext, branch_id: UUID | None = None
) -> tuple[UUID | None, UUID | None]:
    if context.is_platform_admin:
        return None, branch_id
    scoped_branch_id = branch_id
    if context.is_branch_scoped:
        if branch_id is not None and branch_id != context.branch_id:
            raise ForbiddenError("Delivery job branch is outside the caller scope")
        scoped_branch_id = context.branch_id
    return context.organization_id, scoped_branch_id


def _ensure_job_scope(context: AuthorizationContext, job: DeliveryJob) -> None:
    if context.is_platform_admin:
        return
    if job.organization_id != context.organization_id:
        raise ForbiddenError("Delivery job is outside the caller scope")
    if context.is_branch_scoped and job.branch_id != context.branch_id:
        raise ForbiddenError("Delivery job is outside the caller scope")


def _audit(
    db: Session,
    job: DeliveryJob,
    event_type: str,
    actor_user_id: UUID | None,
    *,
    details: dict | None = None,
) -> None:
    event_details = json.dumps(details or {}, default=str) if details else None
    db.add(
        DeliveryAudit(
            delivery_job_id=job.id,
            event_type=event_type,
            event_timestamp=datetime.now(UTC),
            event_details=event_details,
        )
    )
    record_audit_event(
        db,
        event_type,
        actor_user_id,
        "DeliveryJob",
        job.id,
        metadata={
            "domain_event": "".join(part.title() for part in event_type.split(".")[1:]),
            "delivery_job_id": str(job.id),
            "family_id": str(job.family_id),
            "booking_id": str(job.booking_id),
            "gallery_id": str(job.gallery_id),
            "editing_job_id": str(job.editing_job_id),
        }
        | (details or {}),
    )


def _job_to_context(job: DeliveryJob) -> dict:
    return {
        "family_name": job.family.primary_contact_name if job.family else None,
        "booking_number": job.booking.booking_number if job.booking else None,
        "gallery_name": job.gallery.gallery_name if job.gallery else None,
        "service_type": job.editing_job.booking_item.service_type
        if job.editing_job and job.editing_job.booking_item
        else None,
    }


def job_to_read(job: DeliveryJob) -> dict:
    data = {
        "id": job.id,
        "organization_id": job.organization_id,
        "branch_id": job.branch_id,
        "family_id": job.family_id,
        "booking_id": job.booking_id,
        "gallery_id": job.gallery_id,
        "editing_job_id": job.editing_job_id,
        "delivery_number": job.delivery_number,
        "delivery_status": job.delivery_status,
        "edited_photo_count": job.edited_photo_count,
        "delivery_date": job.delivery_date,
        "expiry_date": job.expiry_date,
        "delivery_link": job.delivery_link,
        "download_count": job.download_count,
        "max_downloads": job.max_downloads,
        "allow_re_download": job.allow_re_download,
        "re_download_fee": job.re_download_fee,
        "watermark_enabled": job.watermark_enabled,
        "original_download_enabled": job.original_download_enabled,
        "zip_generation_status": job.zip_generation_status,
        "client_notified_at": job.client_notified_at,
        "last_downloaded_at": job.last_downloaded_at,
        "delivery_notes": job.delivery_notes,
        "deleted_at": job.deleted_at,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
    data.update(_job_to_context(job))
    return data


def client_job_to_read(job: DeliveryJob) -> dict:
    data = job_to_read(job)
    data["remaining_downloads"] = max(job.max_downloads - job.download_count, 0)
    return data


def _expire_if_needed(db: Session, job: DeliveryJob, actor_user_id: UUID | None = None) -> bool:
    if job.delivery_status in {DeliveryStatus.CLOSED.value, DeliveryStatus.EXPIRED.value}:
        return False
    if date.today() <= job.expiry_date:
        return False
    job.delivery_status = DeliveryStatus.EXPIRED.value
    _audit(db, job, "delivery.expired", actor_user_id)
    return True


def create_job_from_editing_job(
    db: Session,
    editing_job: EditingJob,
    *,
    actor_user_id: UUID | None,
    max_downloads: int = DEFAULT_MAX_DOWNLOADS,
    allow_re_download: bool = False,
    re_download_fee: Decimal = Decimal("0"),
    watermark_enabled: bool = True,
    original_download_enabled: bool = False,
    delivery_notes: str | None = None,
    commit: bool = True,
) -> DeliveryJob:
    repository = DeliveryRepository(db)
    existing = repository.get_job_by_editing_job(editing_job.id)
    if existing is not None:
        return existing
    if editing_job.editing_status != EditingStatus.READY_FOR_DELIVERY.value:
        raise ConflictError("Delivery job requires editing job ready for delivery")
    delivery_date = date.today()
    job = DeliveryJob(
        organization_id=editing_job.organization_id,
        branch_id=editing_job.branch_id,
        family_id=editing_job.booking.family_id,
        booking_id=editing_job.booking_id,
        gallery_id=editing_job.gallery_id,
        editing_job_id=editing_job.id,
        delivery_number=repository.next_delivery_number(),
        delivery_status=DeliveryStatus.PENDING.value,
        edited_photo_count=editing_job.completed_photo_count,
        delivery_date=delivery_date,
        expiry_date=delivery_date + timedelta(days=DEFAULT_EXPIRY_DAYS),
        download_count=0,
        max_downloads=max_downloads,
        allow_re_download=allow_re_download,
        re_download_fee=re_download_fee,
        watermark_enabled=watermark_enabled,
        original_download_enabled=original_download_enabled,
        zip_generation_status=ZipGenerationStatus.PENDING.value,
        delivery_notes=delivery_notes,
    )
    repository.create_job(job)
    try:
        db.flush()
        job.delivery_link = f"/client/delivery/{job.id}"
        _audit(db, job, "delivery.job_created", actor_user_id)
        if commit:
            db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Delivery job already exists for this gallery") from exc
    return repository.get_job(job.id) or job


def create_job(
    db: Session, payload: DeliveryJobCreate, context: AuthorizationContext
) -> DeliveryJob:
    editing_job = db.get(EditingJob, payload.editing_job_id)
    if editing_job is None:
        raise NotFoundError("Editing job not found")
    if not context.is_platform_admin:
        if editing_job.organization_id != context.organization_id:
            raise ForbiddenError("Editing job is outside the caller scope")
        if context.is_branch_scoped and editing_job.branch_id != context.branch_id:
            raise ForbiddenError("Editing job is outside the caller scope")
    return create_job_from_editing_job(
        db,
        editing_job,
        actor_user_id=context.user_id,
        max_downloads=payload.max_downloads,
        allow_re_download=payload.allow_re_download,
        re_download_fee=payload.re_download_fee,
        watermark_enabled=payload.watermark_enabled,
        original_download_enabled=payload.original_download_enabled,
        delivery_notes=payload.delivery_notes,
    )


def get_job(db: Session, job_id: UUID, context: AuthorizationContext) -> DeliveryJob:
    job = DeliveryRepository(db).get_job(job_id)
    if job is None:
        raise NotFoundError("Delivery job not found")
    _ensure_job_scope(context, job)
    if _expire_if_needed(db, job, context.user_id):
        db.commit()
        job = DeliveryRepository(db).get_job(job_id) or job
    return job


def get_public_job(db: Session, job_id: UUID) -> DeliveryJob:
    job = DeliveryRepository(db).get_job(job_id)
    if job is None:
        raise NotFoundError("Delivery job not found")
    if _expire_if_needed(db, job):
        db.commit()
        raise GoneError("Delivery has expired")
    if job.delivery_status == DeliveryStatus.EXPIRED.value:
        raise GoneError("Delivery has expired")
    if job.delivery_status not in {
        DeliveryStatus.READY.value,
        DeliveryStatus.SENT.value,
        DeliveryStatus.DELIVERED.value,
        DeliveryStatus.REOPENED.value,
    }:
        raise ConflictError("Delivery is not ready for client access")
    return job


def list_jobs(
    db: Session,
    context: AuthorizationContext,
    *,
    page: int,
    page_size: int,
    branch_id: UUID | None = None,
    status: str | None = None,
    search: str | None = None,
) -> PageResult:
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    return DeliveryRepository(db).list_jobs(
        page=page,
        page_size=page_size,
        organization_id=organization_id,
        branch_id=scoped_branch_id,
        status=status,
        search=search,
    )


def update_job(
    db: Session, job_id: UUID, payload: DeliveryJobUpdate, context: AuthorizationContext
) -> DeliveryJob:
    job = get_job(db, job_id, context)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(job, field, value.value if hasattr(value, "value") else value)
    _audit(db, job, "delivery.updated", context.user_id)
    db.commit()
    return get_job(db, job.id, context)


def generate_zip(db: Session, job_id: UUID, context: AuthorizationContext) -> DeliveryJob:
    job = get_job(db, job_id, context)
    if job.delivery_status not in {
        DeliveryStatus.PENDING.value,
        DeliveryStatus.ZIP_GENERATING.value,
        DeliveryStatus.REOPENED.value,
    }:
        raise ConflictError("Delivery ZIP can only be generated for pending or reopened jobs")
    job.delivery_status = DeliveryStatus.READY.value
    job.zip_generation_status = ZipGenerationStatus.COMPLETED.value
    _audit(db, job, "delivery.zip_generated", context.user_id)
    db.commit()
    return get_job(db, job.id, context)


def send_delivery(db: Session, job_id: UUID, context: AuthorizationContext) -> DeliveryJob:
    job = get_job(db, job_id, context)
    if job.zip_generation_status != ZipGenerationStatus.COMPLETED.value:
        raise ConflictError("Generate delivery ZIP before sending")
    if job.delivery_status not in {DeliveryStatus.READY.value, DeliveryStatus.REOPENED.value}:
        raise ConflictError("Only ready delivery jobs can be sent")
    job.delivery_status = DeliveryStatus.SENT.value
    job.client_notified_at = datetime.now(UTC)
    _audit(db, job, "delivery.sent", context.user_id)
    db.commit()
    return get_job(db, job.id, context)


def record_download(
    db: Session,
    job_id: UUID,
    *,
    ip_address: str | None,
    user_agent: str | None,
) -> DeliveryJob:
    repository = DeliveryRepository(db)
    job = repository.get_job_for_update(job_id)
    if job is None:
        raise NotFoundError("Delivery job not found")
    if _expire_if_needed(db, job):
        db.commit()
        raise GoneError("Delivery has expired")
    if job.delivery_status not in {
        DeliveryStatus.READY.value,
        DeliveryStatus.SENT.value,
        DeliveryStatus.DELIVERED.value,
        DeliveryStatus.REOPENED.value,
    }:
        raise ConflictError("Delivery is not ready for download")
    if job.download_count >= job.max_downloads:
        raise ForbiddenError("Delivery download limit reached")
    now = datetime.now(UTC)
    repository.add_download(
        DeliveryDownload(
            delivery_job_id=job.id,
            downloaded_at=now,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )
    job.download_count += 1
    job.last_downloaded_at = now
    if job.delivery_status in {DeliveryStatus.READY.value, DeliveryStatus.SENT.value}:
        job.delivery_status = DeliveryStatus.DELIVERED.value
    _audit(
        db,
        job,
        "delivery.downloaded",
        None,
        details={"download_count": job.download_count},
    )
    db.commit()
    refreshed = repository.get_job(job.id)
    return refreshed or job


def request_reopen(
    db: Session, job_id: UUID, payload: DeliveryReopenRequest | None = None
) -> DeliveryJob:
    job = DeliveryRepository(db).get_job(job_id)
    if job is None:
        raise NotFoundError("Delivery job not found")
    job.delivery_status = DeliveryStatus.REOPEN_REQUESTED.value
    _audit(
        db,
        job,
        "delivery.reopen_requested",
        None,
        details={"notes": payload.notes if payload else None},
    )
    db.commit()
    refreshed = DeliveryRepository(db).get_job(job.id)
    return refreshed or job


def approve_reopen(db: Session, job_id: UUID, context: AuthorizationContext) -> DeliveryJob:
    job = DeliveryRepository(db).get_job(job_id)
    if job is None:
        raise NotFoundError("Delivery job not found")
    _ensure_job_scope(context, job)
    if job.delivery_status != DeliveryStatus.REOPEN_REQUESTED.value:
        raise ConflictError("Only requested reopen jobs can be approved")
    job.delivery_status = DeliveryStatus.REOPENED.value
    job.allow_re_download = True
    job.expiry_date = date.today() + timedelta(days=DEFAULT_EXPIRY_DAYS)
    _audit(db, job, "delivery.reopened", context.user_id)
    db.commit()
    return get_job(db, job.id, context)


def close_job(db: Session, job_id: UUID, context: AuthorizationContext) -> DeliveryJob:
    job = get_job(db, job_id, context)
    job.delivery_status = DeliveryStatus.CLOSED.value
    _audit(db, job, "delivery.closed", context.user_id)
    db.commit()
    return get_job(db, job.id, context)


def list_downloads(
    db: Session, job_id: UUID, context: AuthorizationContext
) -> list[DeliveryDownload]:
    job = get_job(db, job_id, context)
    return job.downloads


def get_metrics(db: Session, context: AuthorizationContext) -> dict:
    organization_id, branch_id = _scope_filters(context)
    return DeliveryRepository(db).metrics(organization_id, branch_id)
