"""create tenant integrations

Revision ID: 202606100018
Revises: 202606100017
Create Date: 2026-06-11 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100018"
down_revision: str | None = "202606100017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_integrations",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=True),
        sa.Column("provider", sa.String(length=60), nullable=False),
        sa.Column("encrypted_credentials", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("updated_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_integration_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "branch_id",
            "provider",
            name="uq_integration_org_branch_provider",
        ),
    )
    op.create_index(
        op.f("ix_organization_integrations_branch_id"),
        "organization_integrations",
        ["branch_id"],
    )
    op.create_index(
        op.f("ix_organization_integrations_provider"),
        "organization_integrations",
        ["provider"],
    )
    op.create_index(
        op.f("ix_organization_integrations_status"),
        "organization_integrations",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_organization_integrations_status"), table_name="organization_integrations"
    )
    op.drop_index(
        op.f("ix_organization_integrations_provider"),
        table_name="organization_integrations",
    )
    op.drop_index(
        op.f("ix_organization_integrations_branch_id"),
        table_name="organization_integrations",
    )
    op.drop_table("organization_integrations")
