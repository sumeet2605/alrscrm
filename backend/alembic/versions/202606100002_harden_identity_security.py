"""harden identity security

Revision ID: 202606100002
Revises: 202606100001
Create Date: 2026-06-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100002"
down_revision: str | None = "202606100001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    if is_postgresql:
        op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.add_column(
        "roles",
        sa.Column("is_platform", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "roles",
        sa.Column("priority", sa.Integer(), server_default="100", nullable=False),
    )

    op.create_table(
        "refresh_token_sessions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("replaced_by_token_id", sa.Uuid(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["replaced_by_token_id"], ["refresh_token_sessions.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_refresh_token_sessions_user_id"),
        "refresh_token_sessions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_refresh_token_sessions_token_hash"),
        "refresh_token_sessions",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix_refresh_token_sessions_expires_at"),
        "refresh_token_sessions",
        ["expires_at"],
        unique=False,
    )

    op.create_table(
        "audit_logs",
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=True),
        sa.Column("target_id", sa.Uuid(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_logs_actor_user_id"),
        "audit_logs",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_target_id"), "audit_logs", ["target_id"], unique=False)

    op.create_index(
        "uq_organizations_code_lower",
        "organizations",
        [sa.text("lower(code)")],
        unique=True,
    )
    op.create_index(
        "uq_branches_org_code_lower",
        "branches",
        [sa.text("organization_id"), sa.text("lower(code)")],
        unique=True,
    )
    op.create_index(
        "uq_users_org_email_lower",
        "users",
        [sa.text("organization_id"), sa.text("lower(email)")],
        unique=True,
    )

    if is_postgresql:
        _apply_postgresql_defaults_and_constraints()
        op.create_unique_constraint("uq_branch_id_org", "branches", ["id", "organization_id"])
        op.create_foreign_key(
            "fk_user_branch_organization",
            "users",
            "branches",
            ["branch_id", "organization_id"],
            ["id", "organization_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    if is_postgresql:
        op.drop_constraint("fk_user_branch_organization", "users", type_="foreignkey")
        op.drop_constraint("uq_branch_id_org", "branches", type_="unique")
        op.drop_constraint("ck_organizations_code_trimmed", "organizations", type_="check")
        op.drop_constraint("ck_organizations_name_trimmed", "organizations", type_="check")
        op.drop_constraint("ck_branches_code_trimmed", "branches", type_="check")
        op.drop_constraint("ck_branches_name_trimmed", "branches", type_="check")
        op.drop_constraint("ck_users_email_trimmed", "users", type_="check")
        op.drop_constraint("ck_roles_name_trimmed", "roles", type_="check")
        op.drop_constraint("ck_permissions_code_trimmed", "permissions", type_="check")

    op.drop_index("uq_users_org_email_lower", table_name="users")
    op.drop_index("uq_branches_org_code_lower", table_name="branches")
    op.drop_index("uq_organizations_code_lower", table_name="organizations")

    op.drop_index(op.f("ix_audit_logs_target_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_user_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_refresh_token_sessions_expires_at"), table_name="refresh_token_sessions")
    op.drop_index(op.f("ix_refresh_token_sessions_token_hash"), table_name="refresh_token_sessions")
    op.drop_index(op.f("ix_refresh_token_sessions_user_id"), table_name="refresh_token_sessions")
    op.drop_table("refresh_token_sessions")

    op.drop_column("roles", "priority")
    op.drop_column("roles", "is_platform")


def _apply_postgresql_defaults_and_constraints() -> None:
    for table_name in ("organizations", "branches", "users", "roles", "permissions"):
        op.alter_column(table_name, "id", server_default=sa.text("gen_random_uuid()"))

    for table_name in ("organizations", "branches", "users"):
        op.alter_column(table_name, "is_active", server_default=sa.true())

    op.alter_column("refresh_token_sessions", "id", server_default=sa.text("gen_random_uuid()"))
    op.alter_column("audit_logs", "id", server_default=sa.text("gen_random_uuid()"))

    op.create_check_constraint(
        "ck_organizations_code_trimmed", "organizations", "length(trim(code)) > 0"
    )
    op.create_check_constraint(
        "ck_organizations_name_trimmed", "organizations", "length(trim(name)) > 0"
    )
    op.create_check_constraint("ck_branches_code_trimmed", "branches", "length(trim(code)) > 0")
    op.create_check_constraint("ck_branches_name_trimmed", "branches", "length(trim(name)) > 0")
    op.create_check_constraint("ck_users_email_trimmed", "users", "length(trim(email)) > 0")
    op.create_check_constraint("ck_roles_name_trimmed", "roles", "length(trim(name)) > 0")
    op.create_check_constraint(
        "ck_permissions_code_trimmed", "permissions", "length(trim(code)) > 0"
    )
