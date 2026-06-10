"""create booking fulfillment

Revision ID: 202606100007
Revises: 202606100006
Create Date: 2026-06-10 00:07:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100007"
down_revision: str | None = "202606100006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "packages",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("service_type", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("price >= 0", name="ck_package_price_non_negative"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_package_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("branch_id", "name", name="uq_package_branch_name"),
    )
    op.create_index("ix_packages_branch_id", "packages", ["branch_id"])
    op.create_index("ix_packages_service_type", "packages", ["service_type"])

    op.create_table(
        "package_addons",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("price >= 0", name="ck_package_addon_price_non_negative"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_package_addon_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("branch_id", "name", name="uq_package_addon_branch_name"),
    )
    op.create_index("ix_package_addons_branch_id", "package_addons", ["branch_id"])

    op.create_table(
        "bookings",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("booking_number", sa.String(length=40), nullable=False),
        sa.Column("booking_status", sa.String(length=40), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("advance_received", sa.Numeric(12, 2), nullable=False),
        sa.Column("balance_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("total_amount >= 0", name="ck_booking_total_non_negative"),
        sa.CheckConstraint("advance_received >= 0", name="ck_booking_advance_non_negative"),
        sa.CheckConstraint("balance_amount >= 0", name="ck_booking_balance_non_negative"),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_booking_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_number", name="uq_booking_number"),
    )
    op.create_index("ix_bookings_family_id", "bookings", ["family_id"])
    op.create_index("ix_bookings_opportunity_id", "bookings", ["opportunity_id"])
    op.create_index("ix_bookings_booking_status", "bookings", ["booking_status"])
    op.create_index("ix_bookings_booking_date", "bookings", ["booking_date"])
    op.create_index("ix_bookings_branch_date", "bookings", ["branch_id", "booking_date"])

    op.create_table(
        "booking_items",
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("package_id", sa.Uuid(), nullable=False),
        sa.Column("service_type", sa.String(length=40), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False),
        sa.Column("final_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("price >= 0", name="ck_booking_item_price_non_negative"),
        sa.CheckConstraint("discount >= 0", name="ck_booking_item_discount_non_negative"),
        sa.CheckConstraint("final_amount >= 0", name="ck_booking_item_final_non_negative"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["package_id"], ["packages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_booking_items_booking_id", "booking_items", ["booking_id"])
    op.create_index("ix_booking_items_service_type", "booking_items", ["service_type"])

    op.create_table(
        "booking_item_addons",
        sa.Column("booking_item_id", sa.Uuid(), nullable=False),
        sa.Column("addon_id", sa.Uuid(), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_booking_item_addon_price_non_negative"),
        sa.ForeignKeyConstraint(["addon_id"], ["package_addons.id"]),
        sa.ForeignKeyConstraint(["booking_item_id"], ["booking_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_booking_item_addons_booking_item_id", "booking_item_addons", ["booking_item_id"]
    )

    op.create_table(
        "shoot_schedules",
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("booking_item_id", sa.Uuid(), nullable=False),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("shoot_status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("scheduled_end > scheduled_start", name="ck_schedule_end_after_start"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["booking_item_id"], ["booking_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shoot_schedules_booking_id", "shoot_schedules", ["booking_id"])
    op.create_index("ix_shoot_schedules_booking_item_id", "shoot_schedules", ["booking_item_id"])
    op.create_index("ix_shoot_schedules_scheduled_start", "shoot_schedules", ["scheduled_start"])
    op.create_index("ix_shoot_schedules_shoot_status", "shoot_schedules", ["shoot_status"])

    op.create_table(
        "photographer_assignments",
        sa.Column("shoot_schedule_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["shoot_schedule_id"], ["shoot_schedules.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("shoot_schedule_id", "user_id", name="uq_assignment_schedule_user"),
    )
    op.create_index("ix_photographer_assignments_user_id", "photographer_assignments", ["user_id"])
    op.create_index(
        "ix_photographer_assignments_assigned_at", "photographer_assignments", ["assigned_at"]
    )
    op.create_index(
        "ix_photographer_assignments_shoot_schedule_id",
        "photographer_assignments",
        ["shoot_schedule_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_photographer_assignments_shoot_schedule_id", table_name="photographer_assignments"
    )
    op.drop_index("ix_photographer_assignments_assigned_at", table_name="photographer_assignments")
    op.drop_index("ix_photographer_assignments_user_id", table_name="photographer_assignments")
    op.drop_table("photographer_assignments")
    op.drop_index("ix_shoot_schedules_shoot_status", table_name="shoot_schedules")
    op.drop_index("ix_shoot_schedules_scheduled_start", table_name="shoot_schedules")
    op.drop_index("ix_shoot_schedules_booking_item_id", table_name="shoot_schedules")
    op.drop_index("ix_shoot_schedules_booking_id", table_name="shoot_schedules")
    op.drop_table("shoot_schedules")
    op.drop_index("ix_booking_item_addons_booking_item_id", table_name="booking_item_addons")
    op.drop_table("booking_item_addons")
    op.drop_index("ix_booking_items_service_type", table_name="booking_items")
    op.drop_index("ix_booking_items_booking_id", table_name="booking_items")
    op.drop_table("booking_items")
    op.drop_index("ix_bookings_branch_date", table_name="bookings")
    op.drop_index("ix_bookings_booking_date", table_name="bookings")
    op.drop_index("ix_bookings_booking_status", table_name="bookings")
    op.drop_index("ix_bookings_opportunity_id", table_name="bookings")
    op.drop_index("ix_bookings_family_id", table_name="bookings")
    op.drop_table("bookings")
    op.drop_index("ix_package_addons_branch_id", table_name="package_addons")
    op.drop_table("package_addons")
    op.drop_index("ix_packages_service_type", table_name="packages")
    op.drop_index("ix_packages_branch_id", table_name="packages")
    op.drop_table("packages")
