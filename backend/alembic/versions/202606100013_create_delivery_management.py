"""create delivery management

Revision ID: 202606100013
Revises: 202606100012
Create Date: 2026-06-10 03:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100013"
down_revision: str | None = "202606100012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "delivery_jobs",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("gallery_id", sa.Uuid(), nullable=False),
        sa.Column("editing_job_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_number", sa.String(length=40), nullable=False),
        sa.Column("delivery_status", sa.String(length=40), nullable=False),
        sa.Column("edited_photo_count", sa.Integer(), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("delivery_link", sa.Text(), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=False),
        sa.Column("max_downloads", sa.Integer(), nullable=False),
        sa.Column("allow_re_download", sa.Boolean(), nullable=False),
        sa.Column("re_download_fee", sa.Numeric(12, 2), nullable=False),
        sa.Column("watermark_enabled", sa.Boolean(), nullable=False),
        sa.Column("original_download_enabled", sa.Boolean(), nullable=False),
        sa.Column("zip_generation_status", sa.String(length=40), nullable=False),
        sa.Column("client_notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("edited_photo_count >= 0", name="ck_delivery_edited_count_non_negative"),
        sa.CheckConstraint("download_count >= 0", name="ck_delivery_download_count_non_negative"),
        sa.CheckConstraint("max_downloads >= 0", name="ck_delivery_max_downloads_non_negative"),
        sa.CheckConstraint("re_download_fee >= 0", name="ck_delivery_re_download_fee_non_negative"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["editing_job_id"], ["editing_jobs.id"]),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["gallery_id"], ["galleries.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_delivery_job_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_number", name="uq_delivery_job_number"),
        sa.UniqueConstraint("editing_job_id", name="uq_delivery_job_editing_job"),
        sa.UniqueConstraint("gallery_id", name="uq_delivery_job_gallery"),
    )
    op.create_index("ix_delivery_jobs_branch_id", "delivery_jobs", ["branch_id"])
    op.create_index("ix_delivery_jobs_booking_id", "delivery_jobs", ["booking_id"])
    op.create_index("ix_delivery_jobs_delivery_date", "delivery_jobs", ["delivery_date"])
    op.create_index("ix_delivery_jobs_delivery_status", "delivery_jobs", ["delivery_status"])
    op.create_index("ix_delivery_jobs_editing_job_id", "delivery_jobs", ["editing_job_id"])
    op.create_index("ix_delivery_jobs_expiry_date", "delivery_jobs", ["expiry_date"])
    op.create_index("ix_delivery_jobs_family_id", "delivery_jobs", ["family_id"])
    op.create_index("ix_delivery_jobs_gallery_id", "delivery_jobs", ["gallery_id"])
    op.create_index(
        "ix_delivery_jobs_org_branch_status",
        "delivery_jobs",
        ["organization_id", "branch_id", "delivery_status"],
    )
    op.create_index(
        "ix_delivery_jobs_zip_generation_status",
        "delivery_jobs",
        ["zip_generation_status"],
    )

    op.create_table(
        "delivery_downloads",
        sa.Column("delivery_job_id", sa.Uuid(), nullable=False),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["delivery_job_id"], ["delivery_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_delivery_downloads_delivery_job_id",
        "delivery_downloads",
        ["delivery_job_id"],
    )
    op.create_index(
        "ix_delivery_downloads_downloaded_at",
        "delivery_downloads",
        ["downloaded_at"],
    )

    op.create_table(
        "delivery_audits",
        sa.Column("delivery_job_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_details", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["delivery_job_id"], ["delivery_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_delivery_audits_delivery_job_id", "delivery_audits", ["delivery_job_id"])
    op.create_index("ix_delivery_audits_event_timestamp", "delivery_audits", ["event_timestamp"])
    op.create_index("ix_delivery_audits_event_type", "delivery_audits", ["event_type"])


def downgrade() -> None:
    op.drop_index("ix_delivery_audits_event_type", table_name="delivery_audits")
    op.drop_index("ix_delivery_audits_event_timestamp", table_name="delivery_audits")
    op.drop_index("ix_delivery_audits_delivery_job_id", table_name="delivery_audits")
    op.drop_table("delivery_audits")

    op.drop_index("ix_delivery_downloads_downloaded_at", table_name="delivery_downloads")
    op.drop_index("ix_delivery_downloads_delivery_job_id", table_name="delivery_downloads")
    op.drop_table("delivery_downloads")

    op.drop_index("ix_delivery_jobs_zip_generation_status", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_org_branch_status", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_gallery_id", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_family_id", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_expiry_date", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_editing_job_id", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_delivery_status", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_delivery_date", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_booking_id", table_name="delivery_jobs")
    op.drop_index("ix_delivery_jobs_branch_id", table_name="delivery_jobs")
    op.drop_table("delivery_jobs")
