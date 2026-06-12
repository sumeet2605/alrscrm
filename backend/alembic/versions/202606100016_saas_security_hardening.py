"""saas security hardening

Revision ID: 202606100016
Revises: 202606100015
Create Date: 2026-06-11 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100016"
down_revision: str | None = "202606100015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password_reset_required",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.alter_column("users", "password_reset_required", server_default=None)

    op.add_column("audit_logs", sa.Column("organization_id", sa.Uuid(), nullable=True))
    op.add_column("audit_logs", sa.Column("branch_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_audit_logs_organization",
        "audit_logs",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_audit_logs_branch",
        "audit_logs",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_audit_logs_organization_id", "audit_logs", ["organization_id"])
    op.create_index("ix_audit_logs_branch_id", "audit_logs", ["branch_id"])
    op.create_index(
        "ix_audit_logs_organization_created_at",
        "audit_logs",
        ["organization_id", "created_at"],
    )
    op.create_index(
        "ix_audit_logs_branch_created_at",
        "audit_logs",
        ["branch_id", "created_at"],
    )
    op.execute(
        """
        UPDATE audit_logs
        SET organization_id = users.organization_id,
            branch_id = users.branch_id
        FROM users
        WHERE audit_logs.actor_user_id = users.id
        """
    )
    op.execute(
        """
        UPDATE audit_logs
        SET organization_id = NULLIF(metadata_json ->> 'organization_id', '')::uuid
        WHERE organization_id IS NULL
          AND metadata_json::jsonb ? 'organization_id'
          AND metadata_json ->> 'organization_id' ~
            '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        """
    )
    op.execute(
        """
        UPDATE audit_logs
        SET branch_id = NULLIF(metadata_json ->> 'branch_id', '')::uuid
        WHERE branch_id IS NULL
          AND metadata_json::jsonb ? 'branch_id'
          AND metadata_json ->> 'branch_id' ~
            '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        """
    )

    op.create_table(
        "gallery_access_tokens",
        sa.Column("gallery_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["gallery_id"], ["galleries.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_gallery_access_token_hash"),
    )
    op.create_index(
        op.f("ix_gallery_access_tokens_gallery_id"),
        "gallery_access_tokens",
        ["gallery_id"],
    )
    op.create_index(
        op.f("ix_gallery_access_tokens_expires_at"),
        "gallery_access_tokens",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_gallery_access_tokens_expires_at"), table_name="gallery_access_tokens")
    op.drop_index(op.f("ix_gallery_access_tokens_gallery_id"), table_name="gallery_access_tokens")
    op.drop_table("gallery_access_tokens")
    op.drop_index("ix_audit_logs_branch_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_organization_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_branch_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_organization_id", table_name="audit_logs")
    op.drop_constraint("fk_audit_logs_branch", "audit_logs", type_="foreignkey")
    op.drop_constraint("fk_audit_logs_organization", "audit_logs", type_="foreignkey")
    op.drop_column("audit_logs", "branch_id")
    op.drop_column("audit_logs", "organization_id")
    op.drop_column("users", "password_reset_required")
