"""create organization settings

Revision ID: 202606100015
Revises: 202606100014
Create Date: 2026-06-10 05:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100015"
down_revision: str | None = "202606100014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_settings",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("studio_name", sa.String(length=160), nullable=False),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("contact_phone", sa.String(length=30), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("delivery_expiry_default", sa.Integer(), nullable=False),
        sa.Column("gallery_selection_default_limit", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "delivery_expiry_default > 0",
            name="ck_organization_settings_delivery_expiry_positive",
        ),
        sa.CheckConstraint(
            "gallery_selection_default_limit > 0",
            name="ck_organization_settings_gallery_limit_positive",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", name="uq_organization_settings_organization"),
    )
    op.create_index(
        op.f("ix_organization_settings_organization_id"),
        "organization_settings",
        ["organization_id"],
        unique=True,
    )
    op.execute(
        """
        INSERT INTO organization_settings (
            organization_id,
            studio_name,
            timezone,
            currency,
            delivery_expiry_default,
            gallery_selection_default_limit,
            id
        )
        SELECT
            id,
            name,
            'Asia/Kolkata',
            'INR',
            30,
            30,
            gen_random_uuid()
        FROM organizations
        WHERE NOT EXISTS (
            SELECT 1
            FROM organization_settings
            WHERE organization_settings.organization_id = organizations.id
        )
        """
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_organization_settings_organization_id"),
        table_name="organization_settings",
    )
    op.drop_table("organization_settings")
