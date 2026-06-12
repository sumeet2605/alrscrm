from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.editing.enums import EditingPriority, EditingReviewStatus, EditingStatus
from app.editing.models import EditingJob, EditingReview
from app.editing.repositories import EditingRepository
from app.editing.schemas import (
    EditingAssignEditor,
    EditingJobCreate,
    EditingJobUpdate,
    EditingReviewCreate,
)
from app.galleries.enums import GalleryStatus
from app.galleries.models import Gallery
from app.galleries.repositories import GalleryRepository
from app.identity.models import User
from app.identity.policies import AuthorizationContext
from app.shared.exceptions.application import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event

PRIORITY_DAYS: dict[str, int] = {
    EditingPriority.LOW.value: 10,
    EditingPriority.NORMAL.value: 7,
    EditingPriority.HIGH.value: 3,
    EditingPriority.URGENT.value: 1,
}


def _scope_filters(
    context: AuthorizationContext, branch_id: UUID | None = None
) -> tuple[UUID | None, UUID | None]:
    if context.is_platform_admin:
        return None, branch_id
    scoped_branch_id = branch_id
    if context.is_branch_scoped:
        if branch_id is not None and branch_id != context.branch_id:
            raise ForbiddenError("Editing job branch is outside the caller scope")
        scoped_branch_id = context.branch_id
    return context.organization_id, scoped_branch_id


def _is_manager(context: AuthorizationContext) -> bool:
    return (
        context.is_platform_admin
        or context.is_owner
        or "Branch Manager" in context.role_names
        or "Organization Admin" in context.role_names
    )


def _is_editor_limited(context: AuthorizationContext) -> bool:
    return "Editor" in context.role_names and not _is_manager(context)


def _ensure_job_scope(context: AuthorizationContext, job: EditingJob) -> None:
    if context.is_platform_admin:
        return
    if job.organization_id != context.organization_id:
        raise ForbiddenError("Editing job is outside the caller scope")
    if context.is_branch_scoped and job.branch_id != context.branch_id:
        raise ForbiddenError("Editing job is outside the caller scope")
    if _is_editor_limited(context) and job.assigned_editor_id != context.user_id:
        raise ForbiddenError("Editing job is not assigned to the caller")


def _calculate_due_date(priority: str, selection_submitted_at: datetime | None) -> date:
    anchor = selection_submitted_at or datetime.now(UTC)
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=UTC)
    return (anchor + timedelta(days=PRIORITY_DAYS[priority])).date()


def _job_to_read_context(job: EditingJob) -> dict:
    return {
        "gallery_name": job.gallery.gallery_name if job.gallery else None,
        "booking_number": job.booking.booking_number if job.booking else None,
        "family_name": job.booking.family.primary_contact_name
        if job.booking and job.booking.family
        else None,
        "service_type": job.booking_item.service_type if job.booking_item else None,
    }


def job_to_read(job: EditingJob) -> dict:
    data = {
        "id": job.id,
        "organization_id": job.organization_id,
        "branch_id": job.branch_id,
        "booking_id": job.booking_id,
        "booking_item_id": job.booking_item_id,
        "gallery_id": job.gallery_id,
        "assigned_editor_id": job.assigned_editor_id,
        "priority": job.priority,
        "editing_status": job.editing_status,
        "selected_photo_count": job.selected_photo_count,
        "completed_photo_count": job.completed_photo_count,
        "due_date": job.due_date,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "notes": job.notes,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "assigned_editor": job.assigned_editor,
        "reviews": job.reviews,
    }
    data.update(_job_to_read_context(job))
    return data


def _get_gallery_for_creation(
    db: Session, gallery_id: UUID, context: AuthorizationContext
) -> Gallery:
    gallery = GalleryRepository(db).get_gallery(gallery_id)
    if gallery is None:
        raise NotFoundError("Gallery not found")
    if not context.is_platform_admin:
        if gallery.organization_id != context.organization_id:
            raise ForbiddenError("Gallery is outside the caller scope")
        if context.is_branch_scoped and gallery.branch_id != context.branch_id:
            raise ForbiddenError("Gallery is outside the caller scope")
    if gallery.gallery_status != GalleryStatus.SELECTION_SUBMITTED.value:
        raise ConflictError("Editing job requires submitted gallery selection")
    return gallery


def _ensure_editor(db: Session, editor_id: UUID, context: AuthorizationContext) -> User:
    editor = db.get(User, editor_id)
    if editor is None or not editor.is_active:
        raise NotFoundError("Editor not found")
    if not context.is_platform_admin:
        if editor.organization_id != context.organization_id:
            raise ForbiddenError("Editor is outside the caller scope")
        if context.is_branch_scoped and editor.branch_id != context.branch_id:
            raise ForbiddenError("Editor is outside the caller scope")
    role_names = {role.name for role in editor.roles}
    if "Editor" not in role_names:
        raise ValidationError("Assigned user must have Editor role")
    return editor


def create_job_from_gallery(
    db: Session,
    gallery: Gallery,
    *,
    actor_user_id: UUID,
    priority: EditingPriority = EditingPriority.NORMAL,
    due_date: date | None = None,
    assigned_editor_id: UUID | None = None,
    notes: str | None = None,
    commit: bool = True,
) -> EditingJob:
    repository = EditingRepository(db)
    existing = repository.get_job_by_gallery(gallery.id)
    if existing is not None:
        return existing
    selected_count = repository.selected_photo_count(gallery.id)
    status = EditingStatus.ASSIGNED.value if assigned_editor_id else EditingStatus.PENDING.value
    job = EditingJob(
        organization_id=gallery.organization_id,
        branch_id=gallery.branch_id,
        booking_id=gallery.booking_id,
        booking_item_id=gallery.booking_item_id,
        gallery_id=gallery.id,
        assigned_editor_id=assigned_editor_id,
        priority=priority.value,
        editing_status=status,
        selected_photo_count=selected_count,
        completed_photo_count=0,
        due_date=due_date or _calculate_due_date(priority.value, gallery.selection_submitted_at),
        notes=notes,
    )
    repository.create_job(job)
    try:
        db.flush()
        record_audit_event(
            db,
            "editing.job_created",
            actor_user_id,
            "EditingJob",
            job.id,
            metadata={"domain_event": "EditingJobCreated", "gallery_id": str(gallery.id)},
        )
        if assigned_editor_id is not None:
            record_audit_event(
                db,
                "editing.editor_assigned",
                actor_user_id,
                "EditingJob",
                job.id,
                metadata={
                    "domain_event": "EditingEditorAssigned",
                    "assigned_editor_id": str(assigned_editor_id),
                },
            )
        if commit:
            db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Editing job already exists for this gallery") from exc
    return repository.get_job(job.id) or job


def create_job(db: Session, payload: EditingJobCreate, context: AuthorizationContext) -> EditingJob:
    gallery = _get_gallery_for_creation(db, payload.gallery_id, context)
    if payload.assigned_editor_id is not None:
        _ensure_editor(db, payload.assigned_editor_id, context)
    return create_job_from_gallery(
        db,
        gallery,
        actor_user_id=context.user_id,
        priority=payload.priority,
        due_date=payload.due_date,
        assigned_editor_id=payload.assigned_editor_id,
        notes=payload.notes,
    )


def get_job(db: Session, job_id: UUID, context: AuthorizationContext) -> EditingJob:
    job = EditingRepository(db).get_job(job_id)
    if job is None:
        raise NotFoundError("Editing job not found")
    _ensure_job_scope(context, job)
    return job


def list_jobs(
    db: Session,
    context: AuthorizationContext,
    *,
    page: int,
    page_size: int,
    status: str | None = None,
    priority: str | None = None,
    assigned_editor_id: UUID | None = None,
    branch_id: UUID | None = None,
) -> PageResult:
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    if _is_editor_limited(context):
        assigned_editor_id = context.user_id
    return EditingRepository(db).list_jobs(
        page=page,
        page_size=page_size,
        organization_id=organization_id,
        branch_id=scoped_branch_id,
        status=status,
        priority=priority,
        assigned_editor_id=assigned_editor_id,
    )


def update_job(
    db: Session, job_id: UUID, payload: EditingJobUpdate, context: AuthorizationContext
) -> EditingJob:
    job = get_job(db, job_id, context)
    if job.editing_status == EditingStatus.READY_FOR_DELIVERY.value:
        raise BadRequestError("Ready for delivery jobs are read-only")
    updates = payload.model_dump(exclude_unset=True)
    next_status = updates.get("editing_status")
    completed_count = updates.get("completed_photo_count", job.completed_photo_count)
    if completed_count > job.selected_photo_count:
        raise ValidationError("Completed photo count cannot exceed selected photo count")
    if (
        next_status == EditingStatus.READY_FOR_REVIEW
        and completed_count != job.selected_photo_count
    ):
        raise ConflictError("All selected photos must be completed before review")
    if next_status == EditingStatus.READY_FOR_DELIVERY:
        raise ConflictError("Use ready-for-delivery workflow action")
    for field, value in updates.items():
        setattr(job, field, value.value if hasattr(value, "value") else value)
    db.commit()
    return get_job(db, job.id, context)


def assign_editor(
    db: Session, job_id: UUID, payload: EditingAssignEditor, context: AuthorizationContext
) -> EditingJob:
    job = get_job(db, job_id, context)
    if job.editing_status == EditingStatus.READY_FOR_DELIVERY.value:
        raise ConflictError("Cannot assign editor after ready for delivery")
    _ensure_editor(db, payload.assigned_editor_id, context)
    job.assigned_editor_id = payload.assigned_editor_id
    job.editing_status = EditingStatus.ASSIGNED.value
    if payload.due_date is not None:
        job.due_date = payload.due_date
    record_audit_event(
        db,
        "editing.editor_assigned",
        context.user_id,
        "EditingJob",
        job.id,
        metadata={
            "domain_event": "EditingEditorAssigned",
            "assigned_editor_id": str(payload.assigned_editor_id),
        },
    )
    db.commit()
    return get_job(db, job.id, context)


def start_job(db: Session, job_id: UUID, context: AuthorizationContext) -> EditingJob:
    job = get_job(db, job_id, context)
    if job.assigned_editor_id is None:
        raise ConflictError("Assign an editor before starting")
    if job.editing_status not in {EditingStatus.ASSIGNED.value, EditingStatus.REJECTED.value}:
        raise ConflictError("Only assigned or rejected jobs can be started")
    job.editing_status = EditingStatus.IN_PROGRESS.value
    job.started_at = job.started_at or datetime.now(UTC)
    record_audit_event(
        db,
        "editing.started",
        context.user_id,
        "EditingJob",
        job.id,
        metadata={"domain_event": "EditingStarted"},
    )
    db.commit()
    return get_job(db, job.id, context)


def submit_review(db: Session, job_id: UUID, context: AuthorizationContext) -> EditingJob:
    job = get_job(db, job_id, context)
    if job.completed_photo_count != job.selected_photo_count:
        raise ConflictError("All selected photos must be completed before review")
    if job.editing_status != EditingStatus.IN_PROGRESS.value:
        raise ConflictError("Only in-progress jobs can be submitted for review")
    job.editing_status = EditingStatus.READY_FOR_REVIEW.value
    record_audit_event(
        db,
        "editing.review_submitted",
        context.user_id,
        "EditingJob",
        job.id,
        metadata={"domain_event": "EditingReviewSubmitted"},
    )
    db.commit()
    return get_job(db, job.id, context)


def approve_job(
    db: Session, job_id: UUID, payload: EditingReviewCreate, context: AuthorizationContext
) -> EditingJob:
    job = get_job(db, job_id, context)
    if job.editing_status != EditingStatus.READY_FOR_REVIEW.value:
        raise ConflictError("Only jobs ready for review can be approved")
    if job.assigned_editor_id == context.user_id:
        raise ForbiddenError("Editor cannot approve own review")
    review = EditingReview(
        editing_job_id=job.id,
        reviewed_by_user_id=context.user_id,
        review_status=EditingReviewStatus.APPROVED.value,
        review_notes=payload.review_notes,
        reviewed_at=datetime.now(UTC),
    )
    EditingRepository(db).add_review(review)
    job.editing_status = EditingStatus.APPROVED.value
    job.completed_at = datetime.now(UTC)
    record_audit_event(
        db,
        "editing.approved",
        context.user_id,
        "EditingJob",
        job.id,
        metadata={"domain_event": "EditingApproved"},
    )
    db.commit()
    return get_job(db, job.id, context)


def reject_job(
    db: Session, job_id: UUID, payload: EditingReviewCreate, context: AuthorizationContext
) -> EditingJob:
    job = get_job(db, job_id, context)
    if job.editing_status != EditingStatus.READY_FOR_REVIEW.value:
        raise ConflictError("Only jobs ready for review can be rejected")
    if job.assigned_editor_id == context.user_id:
        raise ForbiddenError("Editor cannot reject own review")
    review = EditingReview(
        editing_job_id=job.id,
        reviewed_by_user_id=context.user_id,
        review_status=EditingReviewStatus.REJECTED.value,
        review_notes=payload.review_notes,
        reviewed_at=datetime.now(UTC),
    )
    EditingRepository(db).add_review(review)
    job.editing_status = EditingStatus.REJECTED.value
    record_audit_event(
        db,
        "editing.rejected",
        context.user_id,
        "EditingJob",
        job.id,
        metadata={"domain_event": "EditingRejected"},
    )
    db.commit()
    return get_job(db, job.id, context)


def mark_ready_for_delivery(db: Session, job_id: UUID, context: AuthorizationContext) -> EditingJob:
    job = get_job(db, job_id, context)
    if job.editing_status != EditingStatus.APPROVED.value:
        raise ConflictError("Only approved jobs can be marked ready for delivery")
    job.editing_status = EditingStatus.READY_FOR_DELIVERY.value
    job.completed_at = job.completed_at or datetime.now(UTC)
    record_audit_event(
        db,
        "editing.ready_for_delivery",
        context.user_id,
        "EditingJob",
        job.id,
        metadata={"domain_event": "EditingReadyForDelivery"},
    )
    from app.delivery.services.delivery_service import create_job_from_editing_job

    create_job_from_editing_job(
        db,
        job,
        actor_user_id=context.user_id,
        commit=False,
    )
    db.commit()
    return get_job(db, job.id, context)


def get_metrics(db: Session, context: AuthorizationContext) -> dict:
    organization_id, branch_id = _scope_filters(context)
    return EditingRepository(db).metrics(organization_id, branch_id)


def get_my_work(db: Session, context: AuthorizationContext) -> dict:
    return EditingRepository(db).my_work(
        context.organization_id, context.branch_id, context.user_id
    )
