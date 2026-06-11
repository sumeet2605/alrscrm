"""harden delivery security

Revision ID: 202606100014
Revises: 202606100013
Create Date: 2026-06-10 04:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100014"
down_revision: str | None = "202606100013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS delivery_number_seq START WITH 1 INCREMENT BY 1")
    op.add_column(
        "delivery_audits",
        sa.Column("organization_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "delivery_audits",
        sa.Column("branch_id", sa.Uuid(), nullable=True),
    )
    op.execute(
        """
        UPDATE delivery_audits
        SET organization_id = delivery_jobs.organization_id,
            branch_id = delivery_jobs.branch_id
        FROM delivery_jobs
        WHERE delivery_audits.delivery_job_id = delivery_jobs.id
        """
    )
    op.alter_column("delivery_audits", "organization_id", nullable=False)
    op.alter_column("delivery_audits", "branch_id", nullable=False)
    op.create_foreign_key(
        "fk_delivery_audit_organization",
        "delivery_audits",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_delivery_audit_branch_organization",
        "delivery_audits",
        "branches",
        ["branch_id", "organization_id"],
        ["id", "organization_id"],
    )
    op.create_index("ix_delivery_audits_branch_id", "delivery_audits", ["branch_id"])

    op.add_column(
        "delivery_jobs",
        sa.Column("delivery_password_hash", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "delivery_jobs",
        sa.Column("reopen_requested_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "delivery_access_tokens",
        sa.Column("delivery_job_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["delivery_job_id"], ["delivery_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_delivery_access_token_hash"),
    )
    op.create_index(
        "ix_delivery_access_tokens_delivery_job_id",
        "delivery_access_tokens",
        ["delivery_job_id"],
    )
    op.create_index(
        "ix_delivery_access_tokens_expires_at",
        "delivery_access_tokens",
        ["expires_at"],
    )
    op.create_index(
        "ix_delivery_access_tokens_created_at",
        "delivery_access_tokens",
        ["created_at"],
    )

    op.create_table(
        "delivery_artifacts",
        sa.Column("delivery_job_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_type", sa.String(length=40), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("file_size >= 0", name="ck_delivery_artifact_file_size_non_negative"),
        sa.ForeignKeyConstraint(["delivery_job_id"], ["delivery_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_delivery_artifacts_delivery_job_id",
        "delivery_artifacts",
        ["delivery_job_id"],
    )
    op.create_index(
        "ix_delivery_artifacts_artifact_type",
        "delivery_artifacts",
        ["artifact_type"],
    )
    op.create_index(
        "ix_delivery_artifacts_generated_at",
        "delivery_artifacts",
        ["generated_at"],
    )

    op.create_table(
        "delivery_reopen_attempts",
        sa.Column("delivery_job_id", sa.Uuid(), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["delivery_job_id"], ["delivery_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_delivery_reopen_attempts_delivery_job_id",
        "delivery_reopen_attempts",
        ["delivery_job_id"],
    )
    op.create_index(
        "ix_delivery_reopen_attempts_ip_address",
        "delivery_reopen_attempts",
        ["ip_address"],
    )
    op.create_index(
        "ix_delivery_reopen_attempts_attempted_at",
        "delivery_reopen_attempts",
        ["attempted_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_delivery_reopen_attempts_attempted_at", table_name="delivery_reopen_attempts")
    op.drop_index("ix_delivery_reopen_attempts_ip_address", table_name="delivery_reopen_attempts")
    op.drop_index(
        "ix_delivery_reopen_attempts_delivery_job_id",
        table_name="delivery_reopen_attempts",
    )
    op.drop_table("delivery_reopen_attempts")

    op.drop_index("ix_delivery_artifacts_generated_at", table_name="delivery_artifacts")
    op.drop_index("ix_delivery_artifacts_artifact_type", table_name="delivery_artifacts")
    op.drop_index("ix_delivery_artifacts_delivery_job_id", table_name="delivery_artifacts")
    op.drop_table("delivery_artifacts")

    op.drop_index("ix_delivery_access_tokens_created_at", table_name="delivery_access_tokens")
    op.drop_index("ix_delivery_access_tokens_expires_at", table_name="delivery_access_tokens")
    op.drop_index("ix_delivery_access_tokens_delivery_job_id", table_name="delivery_access_tokens")
    op.drop_table("delivery_access_tokens")

    op.drop_column("delivery_jobs", "reopen_requested_at")
    op.drop_column("delivery_jobs", "delivery_password_hash")
    op.drop_index("ix_delivery_audits_branch_id", table_name="delivery_audits")
    op.drop_constraint(
        "fk_delivery_audit_branch_organization",
        "delivery_audits",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_delivery_audit_organization",
        "delivery_audits",
        type_="foreignkey",
    )
    op.drop_column("delivery_audits", "branch_id")
    op.drop_column("delivery_audits", "organization_id")
    op.execute("DROP SEQUENCE IF EXISTS delivery_number_seq")
