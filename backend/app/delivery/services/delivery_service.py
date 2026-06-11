import json
import secrets
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from io import BytesIO
from uuid import UUID
from zipfile import ZIP_DEFLATED, ZipFile

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_token,
    decode_token,
    hash_password,
    hash_token_identifier,
    verify_password,
)
from app.delivery.enums import DeliveryStatus, ZipGenerationStatus
from app.delivery.models import (
    DeliveryAccessToken,
    DeliveryArtifact,
    DeliveryAudit,
    DeliveryDownload,
    DeliveryJob,
    DeliveryReopenAttempt,
)
from app.delivery.repositories import DeliveryRepository
from app.delivery.schemas import (
    DeliveryAuthenticateRequest,
    DeliveryJobCreate,
    DeliveryJobUpdate,
    DeliveryReopenRequest,
)
from app.editing.enums import EditingStatus
from app.editing.models import EditingJob
from app.galleries.storage import StorageProvider
from app.identity.policies import AuthorizationContext
from app.shared.exceptions.application import (
    ConflictError,
    ForbiddenError,
    GoneError,
    NotFoundError,
    UnauthorizedError,
)
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event

DEFAULT_MAX_DOWNLOADS = 10
DEFAULT_EXPIRY_DAYS = 90
DELIVERY_SESSION_SECONDS = 60 * 60 * 24
REOPEN_RATE_LIMIT_PER_IP_PER_DAY = 5


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


def _domain_event_name(event_type: str) -> str:
    aliases = {
        "delivery.created": "DeliveryCreated",
        "delivery.generated": "DeliveryGenerated",
        "delivery.reopen_approved": "DeliveryReopenApproved",
    }
    if event_type in aliases:
        return aliases[event_type]
    return "".join(part.title() for part in event_type.split(".")[1:])


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
            organization_id=job.organization_id,
            branch_id=job.branch_id,
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
            "domain_event": _domain_event_name(event_type),
            "organization_id": str(job.organization_id),
            "branch_id": str(job.branch_id),
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
        "delivery_access_url": getattr(job, "_delivery_access_url", None),
        "password_required": job.delivery_password_hash is not None,
        "download_count": job.download_count,
        "max_downloads": job.max_downloads,
        "allow_re_download": job.allow_re_download,
        "re_download_fee": job.re_download_fee,
        "watermark_enabled": job.watermark_enabled,
        "original_download_enabled": job.original_download_enabled,
        "zip_generation_status": job.zip_generation_status,
        "client_notified_at": job.client_notified_at,
        "last_downloaded_at": job.last_downloaded_at,
        "reopen_requested_at": job.reopen_requested_at,
        "delivery_notes": job.delivery_notes,
        "deleted_at": job.deleted_at,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "artifacts": job.artifacts,
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


def _token_expiry(job: DeliveryJob) -> datetime:
    return datetime.combine(job.expiry_date + timedelta(days=1), datetime.min.time(), UTC)


def _client_url(raw_token: str) -> str:
    return f"/client/delivery/{raw_token}"


def _generate_raw_access_token() -> str:
    return secrets.token_urlsafe(32)


def _attach_one_time_url(job: DeliveryJob, raw_token: str) -> None:
    job._delivery_access_url = _client_url(raw_token)


def _refetch_with_one_time_url(
    db: Session, job_id: UUID, context: AuthorizationContext, raw_token: str
) -> DeliveryJob:
    refreshed = get_job(db, job_id, context)
    _attach_one_time_url(refreshed, raw_token)
    return refreshed


def _validate_access_token(db: Session, raw_token: str) -> tuple[DeliveryJob, DeliveryAccessToken]:
    repository = DeliveryRepository(db)
    access_token = repository.active_access_token_by_hash(hash_token_identifier(raw_token))
    if access_token is None or access_token.revoked_at is not None:
        raise UnauthorizedError("Invalid delivery access token")
    now = datetime.now(UTC)
    expires_at = access_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        raise UnauthorizedError("Delivery access token has expired")
    job = repository.get_job(access_token.delivery_job_id)
    if job is None:
        raise NotFoundError("Delivery job not found")
    access_token.last_accessed_at = now
    return job, access_token


def rotate_access_token(
    db: Session,
    job: DeliveryJob,
    actor_user_id: UUID | None,
    *,
    revoke_existing: bool = True,
) -> str:
    repository = DeliveryRepository(db)
    now = datetime.now(UTC)
    if revoke_existing:
        for access_token in repository.active_access_tokens_for_job(job.id):
            access_token.revoked_at = now
    raw_token = _generate_raw_access_token()
    repository.add_access_token(
        DeliveryAccessToken(
            delivery_job_id=job.id,
            token_hash=hash_token_identifier(raw_token),
            expires_at=_token_expiry(job),
            created_at=now,
        )
    )
    _audit(db, job, "delivery.access_token_rotated", actor_user_id)
    _attach_one_time_url(job, raw_token)
    return raw_token


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
    password: str | None = None,
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
        delivery_link=None,
        delivery_password_hash=hash_password(password) if password else None,
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
        raw_token = rotate_access_token(db, job, actor_user_id, revoke_existing=False)
        _attach_one_time_url(job, raw_token)
        _audit(db, job, "delivery.created", actor_user_id)
        if commit:
            db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Delivery job already exists for this gallery") from exc
    created = repository.get_job(job.id) or job
    _attach_one_time_url(created, raw_token)
    return created


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
        password=payload.password,
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


def get_public_job_by_token(db: Session, raw_token: str) -> DeliveryJob:
    job, _ = _validate_access_token(db, raw_token)
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
    db.commit()
    return job


def authenticate_public_delivery(
    db: Session, payload: DeliveryAuthenticateRequest
) -> dict[str, str | int]:
    job, _ = _validate_access_token(db, payload.token)
    if job.delivery_password_hash is not None:
        if not payload.password or not verify_password(
            payload.password, job.delivery_password_hash
        ):
            raise UnauthorizedError("Invalid delivery password")
    session_token = create_token(
        job.id,
        "delivery_session",
        expires_delta=timedelta(seconds=DELIVERY_SESSION_SECONDS),
    )
    db.commit()
    return {"session_token": session_token, "expires_in_seconds": DELIVERY_SESSION_SECONDS}


def _validate_delivery_session(session_token: str, job_id: UUID) -> None:
    try:
        payload = decode_token(session_token, "delivery_session")
    except ValueError as exc:
        raise UnauthorizedError("Invalid delivery session") from exc
    if payload.get("sub") != str(job_id):
        raise UnauthorizedError("Invalid delivery session")


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
        if field == "password":
            job.delivery_password_hash = hash_password(value) if value else None
        else:
            setattr(job, field, value)
    _audit(db, job, "delivery.updated", context.user_id)
    db.commit()
    return get_job(db, job.id, context)


def _build_zip_artifact(job: DeliveryJob) -> tuple[bytes, str]:
    buffer = BytesIO()
    manifest = {
        "delivery_number": job.delivery_number,
        "gallery_id": str(job.gallery_id),
        "editing_job_id": str(job.editing_job_id),
        "edited_photo_count": job.edited_photo_count,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
    content = buffer.getvalue()
    return content, sha256(content).hexdigest()


def generate_zip(
    db: Session,
    job_id: UUID,
    context: AuthorizationContext,
    storage_provider: StorageProvider,
) -> DeliveryJob:
    job = get_job(db, job_id, context)
    if job.delivery_status not in {DeliveryStatus.PENDING.value, DeliveryStatus.REOPENED.value}:
        raise ConflictError("Delivery ZIP can only be generated for pending or reopened jobs")
    job.delivery_status = DeliveryStatus.ZIP_GENERATING.value
    job.zip_generation_status = ZipGenerationStatus.GENERATING.value
    db.flush()
    content, checksum = _build_zip_artifact(job)
    storage_key = (
        f"{job.organization_id}/{job.branch_id}/delivery/{job.id}/{job.delivery_number}.zip"
    )
    stored_file = storage_provider.upload_file(storage_key, content, "application/zip")
    DeliveryRepository(db).add_artifact(
        DeliveryArtifact(
            delivery_job_id=job.id,
            artifact_type="ZIP",
            storage_key=stored_file.storage_path,
            checksum=checksum,
            file_size=stored_file.file_size,
            generated_at=datetime.now(UTC),
        )
    )
    job.delivery_status = DeliveryStatus.READY.value
    job.zip_generation_status = ZipGenerationStatus.COMPLETED.value
    _audit(
        db,
        job,
        "delivery.generated",
        context.user_id,
        details={"checksum": checksum, "file_size": stored_file.file_size},
    )
    db.commit()
    return get_job(db, job.id, context)


def send_delivery(db: Session, job_id: UUID, context: AuthorizationContext) -> DeliveryJob:
    job = get_job(db, job_id, context)
    if job.zip_generation_status != ZipGenerationStatus.COMPLETED.value:
        raise ConflictError("Generate delivery ZIP before sending")
    if job.delivery_status not in {DeliveryStatus.READY.value, DeliveryStatus.REOPENED.value}:
        raise ConflictError("Only ready delivery jobs can be sent")
    raw_token = rotate_access_token(db, job, context.user_id)
    job.delivery_status = DeliveryStatus.SENT.value
    job.client_notified_at = datetime.now(UTC)
    _attach_one_time_url(job, raw_token)
    _audit(db, job, "delivery.sent", context.user_id)
    db.commit()
    return _refetch_with_one_time_url(db, job.id, context, raw_token)


def record_download(
    db: Session,
    raw_token: str,
    session_token: str,
    storage_provider: StorageProvider,
    *,
    ip_address: str | None,
    user_agent: str | None,
) -> dict:
    repository = DeliveryRepository(db)
    token_job, _ = _validate_access_token(db, raw_token)
    _validate_delivery_session(session_token, token_job.id)
    job = repository.get_job_for_update(token_job.id)
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
    artifact = repository.latest_artifact(job.id, "ZIP")
    if artifact is None:
        raise ConflictError("Delivery artifact is not ready")
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
        details={"download_count": job.download_count, "ip_address": ip_address},
    )
    db.commit()
    return {
        "download_url": storage_provider.generate_signed_url(artifact.storage_key),
        "download_count": job.download_count,
        "remaining_downloads": max(job.max_downloads - job.download_count, 0),
    }


def request_reopen(
    db: Session,
    raw_token: str,
    payload: DeliveryReopenRequest,
    *,
    ip_address: str | None,
) -> DeliveryJob:
    repository = DeliveryRepository(db)
    job, _ = _validate_access_token(db, raw_token)
    if job.delivery_status != DeliveryStatus.DELIVERED.value:
        raise ConflictError("Only delivered jobs can request reopen")
    now = datetime.now(UTC)
    if (
        repository.reopen_attempts_for_ip(ip_address, now - timedelta(days=1))
        >= REOPEN_RATE_LIMIT_PER_IP_PER_DAY
    ):
        raise ForbiddenError("Reopen request rate limit exceeded")
    if repository.recent_reopen_attempt_for_job(job.id) is not None:
        raise ConflictError("A reopen request already exists within the last 24 hours")
    repository.add_reopen_attempt(
        DeliveryReopenAttempt(delivery_job_id=job.id, ip_address=ip_address, attempted_at=now)
    )
    job.delivery_status = DeliveryStatus.REOPEN_REQUESTED.value
    job.reopen_requested_at = now
    _audit(
        db,
        job,
        "delivery.reopen_requested",
        None,
        details={
            "requested_by_name": payload.requested_by_name,
            "requested_by_email": payload.requested_by_email,
            "reason": payload.reason,
            "ip_address": ip_address,
        },
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
    raw_token = rotate_access_token(db, job, context.user_id)
    _attach_one_time_url(job, raw_token)
    _audit(db, job, "delivery.reopen_approved", context.user_id)
    db.commit()
    return _refetch_with_one_time_url(db, job.id, context, raw_token)


def close_job(db: Session, job_id: UUID, context: AuthorizationContext) -> DeliveryJob:
    job = get_job(db, job_id, context)
    if job.delivery_status == DeliveryStatus.CLOSED.value:
        return job
    if job.delivery_status not in {
        DeliveryStatus.DELIVERED.value,
        DeliveryStatus.EXPIRED.value,
        DeliveryStatus.REOPENED.value,
    }:
        raise ConflictError("Only delivered, expired, or reopened jobs can be closed")
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


def rotate_job_access_token(
    db: Session, job_id: UUID, context: AuthorizationContext
) -> DeliveryJob:
    job = get_job(db, job_id, context)
    raw_token = rotate_access_token(db, job, context.user_id)
    _attach_one_time_url(job, raw_token)
    db.commit()
    return _refetch_with_one_time_url(db, job.id, context, raw_token)


def revoke_access_tokens(db: Session, job_id: UUID, context: AuthorizationContext) -> DeliveryJob:
    job = get_job(db, job_id, context)
    now = datetime.now(UTC)
    for access_token in DeliveryRepository(db).active_access_tokens_for_job(job.id):
        access_token.revoked_at = now
    _audit(db, job, "delivery.access_token_revoked", context.user_id)
    db.commit()
    return get_job(db, job.id, context)
