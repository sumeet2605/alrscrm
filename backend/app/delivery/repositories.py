from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload, selectinload

from app.bookings.models import Booking
from app.delivery.enums import DeliveryStatus
from app.delivery.models import (
    DeliveryAccessToken,
    DeliveryArtifact,
    DeliveryAudit,
    DeliveryDownload,
    DeliveryJob,
    DeliveryReopenAttempt,
)
from app.editing.models import EditingJob
from app.galleries.models import Gallery
from app.shared.pagination import PageResult, paginate_query


class DeliveryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def job_options(self):
        return (
            joinedload(DeliveryJob.family),
            joinedload(DeliveryJob.booking),
            joinedload(DeliveryJob.gallery),
            joinedload(DeliveryJob.editing_job).joinedload(EditingJob.booking_item),
            selectinload(DeliveryJob.downloads),
            selectinload(DeliveryJob.audits),
            selectinload(DeliveryJob.artifacts),
        )

    def get_job(self, job_id: UUID) -> DeliveryJob | None:
        return (
            self.db.query(DeliveryJob)
            .options(*self.job_options())
            .filter(DeliveryJob.id == job_id, DeliveryJob.deleted_at.is_(None))
            .one_or_none()
        )

    def get_job_for_update(self, job_id: UUID) -> DeliveryJob | None:
        return (
            self.db.query(DeliveryJob)
            .filter(DeliveryJob.id == job_id, DeliveryJob.deleted_at.is_(None))
            .with_for_update()
            .one_or_none()
        )

    def get_job_by_gallery(self, gallery_id: UUID) -> DeliveryJob | None:
        return (
            self.db.query(DeliveryJob)
            .options(*self.job_options())
            .filter(DeliveryJob.gallery_id == gallery_id, DeliveryJob.deleted_at.is_(None))
            .one_or_none()
        )

    def get_job_by_editing_job(self, editing_job_id: UUID) -> DeliveryJob | None:
        return (
            self.db.query(DeliveryJob)
            .options(*self.job_options())
            .filter(
                DeliveryJob.editing_job_id == editing_job_id,
                DeliveryJob.deleted_at.is_(None),
            )
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
        search: str | None = None,
    ) -> PageResult:
        query = self.db.query(DeliveryJob).options(*self.job_options())
        query = self._apply_scope(query, organization_id, branch_id)
        query = query.filter(DeliveryJob.deleted_at.is_(None))
        if status is not None:
            query = query.filter(DeliveryJob.delivery_status == status)
        if search:
            needle = f"%{search.strip().lower()}%"
            query = (
                query.join(Booking, DeliveryJob.booking_id == Booking.id)
                .join(Gallery, DeliveryJob.gallery_id == Gallery.id)
                .filter(
                    func.lower(DeliveryJob.delivery_number).like(needle)
                    | func.lower(Booking.booking_number).like(needle)
                    | func.lower(Gallery.gallery_name).like(needle)
                )
            )
        return paginate_query(
            query.order_by(DeliveryJob.delivery_date.desc(), DeliveryJob.created_at.desc()),
            page,
            page_size,
        )

    def create_job(self, job: DeliveryJob) -> DeliveryJob:
        self.db.add(job)
        return job

    def add_download(self, download: DeliveryDownload) -> DeliveryDownload:
        self.db.add(download)
        return download

    def add_audit(self, audit: DeliveryAudit) -> DeliveryAudit:
        self.db.add(audit)
        return audit

    def add_access_token(self, access_token: DeliveryAccessToken) -> DeliveryAccessToken:
        self.db.add(access_token)
        return access_token

    def active_access_token_by_hash(self, token_hash: str) -> DeliveryAccessToken | None:
        return (
            self.db.query(DeliveryAccessToken)
            .filter(DeliveryAccessToken.token_hash == token_hash)
            .one_or_none()
        )

    def active_access_tokens_for_job(self, job_id: UUID) -> list[DeliveryAccessToken]:
        return (
            self.db.query(DeliveryAccessToken)
            .filter(
                DeliveryAccessToken.delivery_job_id == job_id,
                DeliveryAccessToken.revoked_at.is_(None),
            )
            .all()
        )

    def add_artifact(self, artifact: DeliveryArtifact) -> DeliveryArtifact:
        self.db.add(artifact)
        return artifact

    def latest_artifact(self, job_id: UUID, artifact_type: str) -> DeliveryArtifact | None:
        return (
            self.db.query(DeliveryArtifact)
            .filter(
                DeliveryArtifact.delivery_job_id == job_id,
                DeliveryArtifact.artifact_type == artifact_type,
            )
            .order_by(DeliveryArtifact.generated_at.desc())
            .first()
        )

    def add_reopen_attempt(self, attempt: DeliveryReopenAttempt) -> DeliveryReopenAttempt:
        self.db.add(attempt)
        return attempt

    def reopen_attempts_for_ip(self, ip_address: str | None, since: datetime) -> int:
        query = self.db.query(func.count(DeliveryReopenAttempt.id)).filter(
            DeliveryReopenAttempt.attempted_at >= since
        )
        if ip_address is None:
            query = query.filter(DeliveryReopenAttempt.ip_address.is_(None))
        else:
            query = query.filter(DeliveryReopenAttempt.ip_address == ip_address)
        return int(query.scalar() or 0)

    def recent_reopen_attempt_for_job(self, job_id: UUID) -> DeliveryReopenAttempt | None:
        since = datetime.now(UTC) - timedelta(hours=24)
        return (
            self.db.query(DeliveryReopenAttempt)
            .filter(
                DeliveryReopenAttempt.delivery_job_id == job_id,
                DeliveryReopenAttempt.attempted_at >= since,
            )
            .order_by(DeliveryReopenAttempt.attempted_at.desc())
            .first()
        )

    def next_delivery_number(self) -> str:
        year = datetime.now(UTC).year
        if self.db.bind and self.db.bind.dialect.name == "postgresql":
            sequence_value = self.db.execute(
                text("SELECT nextval('delivery_number_seq')")
            ).scalar_one()
            return f"DLV-{year}-{int(sequence_value):06d}"
        count = self.db.query(DeliveryJob).count() + 1
        return f"DLV-{year}-{count:06d}"

    def metrics(self, organization_id: UUID | None, branch_id: UUID | None) -> dict:
        today = date.today()
        month_start = today.replace(day=1)
        query = self._apply_scope(self.db.query(DeliveryJob), organization_id, branch_id)
        query = query.filter(DeliveryJob.deleted_at.is_(None))

        def count_status(status: DeliveryStatus) -> int:
            return query.filter(DeliveryJob.delivery_status == status.value).count()

        tat_rows = (
            self._apply_scope(
                self.db.query(DeliveryJob.delivery_date, EditingJob.completed_at).join(
                    EditingJob, DeliveryJob.editing_job_id == EditingJob.id
                ),
                organization_id,
                branch_id,
            )
            .filter(DeliveryJob.deleted_at.is_(None), EditingJob.completed_at.is_not(None))
            .all()
        )
        delivery_tat = [
            (delivery_date - completed_at.date()).days
            for delivery_date, completed_at in tat_rows
            if delivery_date is not None and completed_at is not None
        ]

        downloads_this_month = (
            self._apply_scope(
                self.db.query(func.count(DeliveryDownload.id)).join(DeliveryJob),
                organization_id,
                branch_id,
            )
            .filter(
                DeliveryJob.deleted_at.is_(None),
                DeliveryDownload.downloaded_at
                >= datetime.combine(month_start, datetime.min.time(), UTC),
            )
            .scalar()
            or 0
        )
        revenue_potential = query.filter(
            DeliveryJob.delivery_status == DeliveryStatus.REOPEN_REQUESTED.value
        ).with_entities(
            func.coalesce(func.sum(DeliveryJob.re_download_fee), 0)
        ).scalar() or Decimal("0")
        return {
            "pending_delivery": count_status(DeliveryStatus.PENDING),
            "ready_delivery": count_status(DeliveryStatus.READY),
            "delivered": count_status(DeliveryStatus.DELIVERED),
            "expired": count_status(DeliveryStatus.EXPIRED),
            "reopened": query.filter(
                DeliveryJob.delivery_status.in_(
                    [DeliveryStatus.REOPEN_REQUESTED.value, DeliveryStatus.REOPENED.value]
                )
            ).count(),
            "average_delivery_tat": round(sum(delivery_tat) / len(delivery_tat), 2)
            if delivery_tat
            else 0,
            "downloads_this_month": int(downloads_this_month),
            "re_download_revenue_potential": revenue_potential,
        }

    @staticmethod
    def _apply_scope(query, organization_id: UUID | None, branch_id: UUID | None):
        if organization_id is not None:
            query = query.filter(DeliveryJob.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(DeliveryJob.branch_id == branch_id)
        return query
