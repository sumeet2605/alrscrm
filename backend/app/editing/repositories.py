from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.bookings.models import Booking, BookingItem
from app.editing.enums import EditingStatus
from app.editing.models import EditingJob, EditingReview
from app.galleries.models import FavoriteSelection
from app.identity.models import User
from app.shared.pagination import PageResult, paginate_query


class EditingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _elapsed_days(self, start: datetime, end: datetime) -> float:
        if start.tzinfo is None:
            start = start.replace(tzinfo=UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=UTC)
        return (end.astimezone(UTC) - start.astimezone(UTC)).total_seconds() / 86400

    def job_options(self):
        return (
            joinedload(EditingJob.assigned_editor),
            joinedload(EditingJob.gallery),
            joinedload(EditingJob.booking).joinedload(Booking.family),
            joinedload(EditingJob.booking_item),
            selectinload(EditingJob.reviews).joinedload(EditingReview.reviewed_by_user),
        )

    def get_job(self, job_id: UUID) -> EditingJob | None:
        return (
            self.db.query(EditingJob)
            .options(*self.job_options())
            .filter(EditingJob.id == job_id)
            .one_or_none()
        )

    def get_job_by_gallery(self, gallery_id: UUID) -> EditingJob | None:
        return (
            self.db.query(EditingJob)
            .options(*self.job_options())
            .filter(EditingJob.gallery_id == gallery_id)
            .one_or_none()
        )

    def list_jobs(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None,
        branch_id: UUID | None,
        status: str | None = None,
        priority: str | None = None,
        assigned_editor_id: UUID | None = None,
    ) -> PageResult:
        query = self.db.query(EditingJob).options(*self.job_options())
        query = self._apply_scope(query, organization_id, branch_id)
        if status is not None:
            query = query.filter(EditingJob.editing_status == status)
        if priority is not None:
            query = query.filter(EditingJob.priority == priority)
        if assigned_editor_id is not None:
            query = query.filter(EditingJob.assigned_editor_id == assigned_editor_id)
        return paginate_query(
            query.order_by(EditingJob.due_date, EditingJob.created_at), page, page_size
        )

    def create_job(self, job: EditingJob) -> EditingJob:
        self.db.add(job)
        return job

    def add_review(self, review: EditingReview) -> EditingReview:
        self.db.add(review)
        return review

    def selected_photo_count(self, gallery_id: UUID) -> int:
        return int(
            self.db.query(func.count(FavoriteSelection.id))
            .filter(FavoriteSelection.gallery_id == gallery_id)
            .scalar()
            or 0
        )

    def metrics(self, organization_id: UUID | None, branch_id: UUID | None) -> dict:
        today = date.today()
        month_start = today.replace(day=1)
        query = self._apply_scope(self.db.query(EditingJob), organization_id, branch_id)

        def count_status(status: EditingStatus) -> int:
            return query.filter(EditingJob.editing_status == status.value).count()

        completed_jobs = query.filter(
            EditingJob.started_at.is_not(None),
            EditingJob.completed_at.is_not(None),
        ).all()
        editing_tat = [
            self._elapsed_days(job.started_at, job.completed_at)
            for job in completed_jobs
            if job.started_at is not None and job.completed_at is not None
        ]
        review_rows = (
            self._apply_scope(
                self.db.query(EditingJob).join(EditingReview),
                organization_id,
                branch_id,
            )
            .filter(EditingJob.started_at.is_not(None))
            .with_entities(EditingJob.started_at, EditingReview.reviewed_at)
            .all()
        )
        review_tat = [
            self._elapsed_days(started_at, reviewed_at)
            for started_at, reviewed_at in review_rows
            if started_at is not None and reviewed_at is not None
        ]

        editor_rows = (
            self._apply_scope(
                self.db.query(
                    func.coalesce(User.email, "Unassigned"),
                    func.count(EditingJob.id),
                ).outerjoin(User, EditingJob.assigned_editor_id == User.id),
                organization_id,
                branch_id,
            )
            .group_by(User.email)
            .all()
        )
        priority_rows = (
            query.with_entities(EditingJob.priority, func.count(EditingJob.id))
            .group_by(EditingJob.priority)
            .all()
        )
        service_rows = (
            self._apply_scope(
                self.db.query(BookingItem.service_type, func.count(EditingJob.id)).join(
                    EditingJob, EditingJob.booking_item_id == BookingItem.id
                ),
                organization_id,
                branch_id,
            )
            .group_by(BookingItem.service_type)
            .all()
        )
        photos_edited = (
            query.filter(
                EditingJob.completed_at >= datetime.combine(month_start, datetime.min.time(), UTC)
            )
            .with_entities(func.sum(EditingJob.completed_photo_count))
            .scalar()
            or 0
        )
        return {
            "pending_jobs": count_status(EditingStatus.PENDING),
            "assigned_jobs": count_status(EditingStatus.ASSIGNED),
            "in_progress_jobs": count_status(EditingStatus.IN_PROGRESS),
            "ready_for_review": count_status(EditingStatus.READY_FOR_REVIEW),
            "ready_for_delivery": count_status(EditingStatus.READY_FOR_DELIVERY),
            "overdue_jobs": query.filter(
                EditingJob.due_date < today,
                EditingJob.editing_status.notin_(
                    [EditingStatus.READY_FOR_DELIVERY.value, EditingStatus.APPROVED.value]
                ),
            ).count(),
            "average_editing_tat": round(sum(editing_tat) / len(editing_tat), 2)
            if editing_tat
            else 0,
            "average_review_tat": round(sum(review_tat) / len(review_tat), 2) if review_tat else 0,
            "jobs_by_editor": {str(editor): count for editor, count in editor_rows},
            "jobs_by_priority": {str(priority): count for priority, count in priority_rows},
            "jobs_by_service_type": {str(service): count for service, count in service_rows},
            "photos_edited_this_month": int(photos_edited),
        }

    def my_work(self, organization_id: UUID, branch_id: UUID | None, user_id: UUID) -> dict:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        query = self.db.query(EditingJob).filter(
            EditingJob.organization_id == organization_id,
            EditingJob.assigned_editor_id == user_id,
        )
        if branch_id is not None:
            query = query.filter(EditingJob.branch_id == branch_id)
        active_statuses = [
            EditingStatus.ASSIGNED.value,
            EditingStatus.IN_PROGRESS.value,
            EditingStatus.REJECTED.value,
        ]
        return {
            "assigned_jobs": query.filter(
                EditingJob.editing_status == EditingStatus.ASSIGNED.value
            ).count(),
            "due_today": query.filter(EditingJob.due_date == today).count(),
            "overdue": query.filter(
                EditingJob.due_date < today,
                EditingJob.editing_status.in_(active_statuses),
            ).count(),
            "completed_this_week": query.filter(
                EditingJob.completed_at >= datetime.combine(week_start, datetime.min.time(), UTC)
            ).count(),
            "current_workload": query.filter(
                EditingJob.editing_status.in_(active_statuses)
            ).count(),
        }

    @staticmethod
    def _apply_scope(query, organization_id: UUID | None, branch_id: UUID | None):
        if organization_id is not None:
            query = query.filter(EditingJob.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(EditingJob.branch_id == branch_id)
        return query
