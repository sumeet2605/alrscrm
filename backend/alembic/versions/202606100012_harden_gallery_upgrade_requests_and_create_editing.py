"""harden gallery upgrade requests and create editing

Revision ID: 202606100012
Revises: 202606100011
Create Date: 2026-06-10 02:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100012"
down_revision: str | None = "202606100011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("gallery_upgrade_requests", sa.Column("organization_id", sa.Uuid(), nullable=True))
    op.add_column("gallery_upgrade_requests", sa.Column("branch_id", sa.Uuid(), nullable=True))

    op.execute(
        """
        UPDATE gallery_upgrade_requests gur
        SET organization_id = galleries.organization_id,
            branch_id = galleries.branch_id
        FROM galleries
        WHERE gur.gallery_id = galleries.id
        """
    )

    op.alter_column("gallery_upgrade_requests", "organization_id", nullable=False)
    op.alter_column("gallery_upgrade_requests", "branch_id", nullable=False)
    op.create_index(
        "ix_gallery_upgrade_requests_branch_id",
        "gallery_upgrade_requests",
        ["branch_id"],
    )
    op.create_foreign_key(
        "fk_gallery_upgrade_request_branch_organization",
        "gallery_upgrade_requests",
        "branches",
        ["branch_id", "organization_id"],
        ["id", "organization_id"],
    )
    op.create_foreign_key(
        "fk_gallery_upgrade_request_organization",
        "gallery_upgrade_requests",
        "organizations",
        ["organization_id"],
        ["id"],
    )

    op.create_table(
        "editing_jobs",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("booking_item_id", sa.Uuid(), nullable=False),
        sa.Column("gallery_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_editor_id", sa.Uuid(), nullable=True),
        sa.Column("priority", sa.String(length=40), nullable=False),
        sa.Column("editing_status", sa.String(length=40), nullable=False),
        sa.Column("selected_photo_count", sa.Integer(), nullable=False),
        sa.Column("completed_photo_count", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("selected_photo_count >= 0", name="ck_editing_selected_photo_count_non_negative"),
        sa.CheckConstraint("completed_photo_count >= 0", name="ck_editing_completed_photo_count_non_negative"),
        sa.CheckConstraint(
            "completed_photo_count <= selected_photo_count",
            name="ck_editing_completed_not_over_selected",
        ),
        sa.ForeignKeyConstraint(["assigned_editor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["booking_item_id"], ["booking_items.id"]),
        sa.ForeignKeyConstraint(["gallery_id"], ["galleries.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_editing_job_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("gallery_id", name="uq_editing_job_gallery"),
    )
    op.create_index("ix_editing_jobs_assigned_editor_id", "editing_jobs", ["assigned_editor_id"])
    op.create_index("ix_editing_jobs_branch_id", "editing_jobs", ["branch_id"])
    op.create_index("ix_editing_jobs_booking_id", "editing_jobs", ["booking_id"])
    op.create_index("ix_editing_jobs_booking_item_id", "editing_jobs", ["booking_item_id"])
    op.create_index("ix_editing_jobs_due_date", "editing_jobs", ["due_date"])
    op.create_index("ix_editing_jobs_editing_status", "editing_jobs", ["editing_status"])
    op.create_index("ix_editing_jobs_gallery_id", "editing_jobs", ["gallery_id"])
    op.create_index(
        "ix_editing_jobs_org_branch_status",
        "editing_jobs",
        ["organization_id", "branch_id", "editing_status"],
    )

    op.create_table(
        "editing_reviews",
        sa.Column("editing_job_id", sa.Uuid(), nullable=False),
        sa.Column("reviewed_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("review_status", sa.String(length=40), nullable=False),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["editing_job_id"], ["editing_jobs.id"]),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_editing_reviews_editing_job_id", "editing_reviews", ["editing_job_id"])
    op.create_index("ix_editing_reviews_reviewed_by_user_id", "editing_reviews", ["reviewed_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_editing_reviews_reviewed_by_user_id", table_name="editing_reviews")
    op.drop_index("ix_editing_reviews_editing_job_id", table_name="editing_reviews")
    op.drop_table("editing_reviews")

    op.drop_index("ix_editing_jobs_org_branch_status", table_name="editing_jobs")
    op.drop_index("ix_editing_jobs_gallery_id", table_name="editing_jobs")
    op.drop_index("ix_editing_jobs_editing_status", table_name="editing_jobs")
    op.drop_index("ix_editing_jobs_due_date", table_name="editing_jobs")
    op.drop_index("ix_editing_jobs_booking_item_id", table_name="editing_jobs")
    op.drop_index("ix_editing_jobs_booking_id", table_name="editing_jobs")
    op.drop_index("ix_editing_jobs_branch_id", table_name="editing_jobs")
    op.drop_index("ix_editing_jobs_assigned_editor_id", table_name="editing_jobs")
    op.drop_table("editing_jobs")

    op.drop_constraint(
        "fk_gallery_upgrade_request_organization",
        "gallery_upgrade_requests",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_gallery_upgrade_request_branch_organization",
        "gallery_upgrade_requests",
        type_="foreignkey",
    )
    op.drop_index("ix_gallery_upgrade_requests_branch_id", table_name="gallery_upgrade_requests")
    op.drop_column("gallery_upgrade_requests", "branch_id")
    op.drop_column("gallery_upgrade_requests", "organization_id")
