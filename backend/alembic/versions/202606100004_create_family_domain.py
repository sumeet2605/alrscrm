"""create family domain

Revision ID: 202606100004
Revises: 202606100003
Create Date: 2026-06-10 00:04:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100004"
down_revision: str | None = "202606100003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE SEQUENCE IF NOT EXISTS family_code_seq START WITH 1 INCREMENT BY 1")

    op.create_table(
        "families",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("family_code", sa.String(length=20), nullable=False),
        sa.Column("primary_contact_name", sa.String(length=160), nullable=False),
        sa.Column("primary_contact_phone", sa.String(length=30), nullable=False),
        sa.Column("primary_contact_email", sa.String(length=255), nullable=True),
        sa.Column("partner_name", sa.String(length=160), nullable=True),
        sa.Column("partner_phone", sa.String(length=30), nullable=True),
        sa.Column("partner_email", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("expected_delivery_date", sa.Date(), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_family_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("family_code", name="uq_families_family_code"),
        sa.UniqueConstraint("primary_contact_phone", name="uq_families_primary_contact_phone"),
    )
    op.create_index("ix_families_branch_id", "families", ["branch_id"])
    op.create_index("ix_families_created_at", "families", ["created_at"])
    op.create_index("ix_families_expected_delivery_date", "families", ["expected_delivery_date"])
    op.create_index("ix_families_family_code", "families", ["family_code"])
    op.create_index("ix_families_primary_contact_email", "families", ["primary_contact_email"])
    op.create_index("ix_families_primary_contact_phone", "families", ["primary_contact_phone"])
    op.create_index("ix_families_source", "families", ["source"])
    op.create_index("ix_families_status", "families", ["status"])

    op.create_table(
        "family_members",
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("relationship", sa.String(length=40), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=40), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_family_members_family_id", "family_members", ["family_id"])

    op.create_table(
        "family_addresses",
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("address_line_1", sa.String(length=255), nullable=False),
        sa.Column("address_line_2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("country", sa.String(length=120), nullable=False),
        sa.Column("postal_code", sa.String(length=30), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("family_id"),
    )

    op.create_table(
        "family_tags",
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "service_interests",
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("service_type", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_interests_family_id", "service_interests", ["family_id"])

    op.create_table(
        "family_tag_mappings",
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["family_tags.id"]),
        sa.PrimaryKeyConstraint("family_id", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("family_tag_mappings")
    op.drop_index("ix_service_interests_family_id", table_name="service_interests")
    op.drop_table("service_interests")
    op.drop_table("family_tags")
    op.drop_table("family_addresses")
    op.drop_index("ix_family_members_family_id", table_name="family_members")
    op.drop_table("family_members")
    op.drop_index("ix_families_status", table_name="families")
    op.drop_index("ix_families_source", table_name="families")
    op.drop_index("ix_families_primary_contact_phone", table_name="families")
    op.drop_index("ix_families_primary_contact_email", table_name="families")
    op.drop_index("ix_families_family_code", table_name="families")
    op.drop_index("ix_families_expected_delivery_date", table_name="families")
    op.drop_index("ix_families_created_at", table_name="families")
    op.drop_index("ix_families_branch_id", table_name="families")
    op.drop_table("families")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP SEQUENCE IF EXISTS family_code_seq")
