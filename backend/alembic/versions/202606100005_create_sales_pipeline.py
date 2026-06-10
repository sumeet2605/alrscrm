"""create sales pipeline

Revision ID: 202606100005
Revises: 202606100004
Create Date: 2026-06-10 00:05:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100005"
down_revision: str | None = "202606100004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lost_reasons",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "opportunities",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_to_user_id", sa.Uuid(), nullable=False),
        sa.Column("opportunity_type", sa.String(length=40), nullable=False),
        sa.Column("current_stage", sa.String(length=40), nullable=False),
        sa.Column("estimated_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("probability", sa.Integer(), nullable=False),
        sa.Column("expected_booking_date", sa.Date(), nullable=True),
        sa.Column("lost_reason_id", sa.Uuid(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["lost_reason_id"], ["lost_reasons.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_opportunity_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_opportunities_assigned_to_user_id", "opportunities", ["assigned_to_user_id"]
    )
    op.create_index("ix_opportunities_created_at", "opportunities", ["created_at"])
    op.create_index("ix_opportunities_current_stage", "opportunities", ["current_stage"])
    op.create_index(
        "ix_opportunities_expected_booking_date", "opportunities", ["expected_booking_date"]
    )
    op.create_index("ix_opportunities_family_id", "opportunities", ["family_id"])
    op.create_index("ix_opportunities_opportunity_type", "opportunities", ["opportunity_type"])

    op.create_table(
        "followups",
        sa.Column("opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_to_user_id", sa.Uuid(), nullable=False),
        sa.Column("followup_type", sa.String(length=40), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_followups_assigned_to_user_id", "followups", ["assigned_to_user_id"])
    op.create_index("ix_followups_due_date", "followups", ["due_date"])
    op.create_index("ix_followups_opportunity_id", "followups", ["opportunity_id"])
    op.create_index("ix_followups_status", "followups", ["status"])

    op.create_table(
        "opportunity_notes",
        sa.Column("opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_opportunity_notes_created_by_user_id", "opportunity_notes", ["created_by_user_id"]
    )
    op.create_index("ix_opportunity_notes_opportunity_id", "opportunity_notes", ["opportunity_id"])

    op.create_table(
        "opportunity_stage_history",
        sa.Column("opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("from_stage", sa.String(length=40), nullable=True),
        sa.Column("to_stage", sa.String(length=40), nullable=False),
        sa.Column("changed_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_opportunity_stage_history_changed_by_user_id",
        "opportunity_stage_history",
        ["changed_by_user_id"],
    )
    op.create_index(
        "ix_opportunity_stage_history_created_at", "opportunity_stage_history", ["created_at"]
    )
    op.create_index(
        "ix_opportunity_stage_history_opportunity_id",
        "opportunity_stage_history",
        ["opportunity_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_opportunity_stage_history_opportunity_id", table_name="opportunity_stage_history"
    )
    op.drop_index("ix_opportunity_stage_history_created_at", table_name="opportunity_stage_history")
    op.drop_index(
        "ix_opportunity_stage_history_changed_by_user_id",
        table_name="opportunity_stage_history",
    )
    op.drop_table("opportunity_stage_history")
    op.drop_index("ix_opportunity_notes_opportunity_id", table_name="opportunity_notes")
    op.drop_index("ix_opportunity_notes_created_by_user_id", table_name="opportunity_notes")
    op.drop_table("opportunity_notes")
    op.drop_index("ix_followups_status", table_name="followups")
    op.drop_index("ix_followups_opportunity_id", table_name="followups")
    op.drop_index("ix_followups_due_date", table_name="followups")
    op.drop_index("ix_followups_assigned_to_user_id", table_name="followups")
    op.drop_table("followups")
    op.drop_index("ix_opportunities_opportunity_type", table_name="opportunities")
    op.drop_index("ix_opportunities_family_id", table_name="opportunities")
    op.drop_index("ix_opportunities_expected_booking_date", table_name="opportunities")
    op.drop_index("ix_opportunities_current_stage", table_name="opportunities")
    op.drop_index("ix_opportunities_created_at", table_name="opportunities")
    op.drop_index("ix_opportunities_assigned_to_user_id", table_name="opportunities")
    op.drop_table("opportunities")
    op.drop_table("lost_reasons")
