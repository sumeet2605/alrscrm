"""harden sales pipeline

Revision ID: 202606100006
Revises: 202606100005
Create Date: 2026-06-10 00:06:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "202606100006"
down_revision: str | None = "202606100005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_opportunity_probability_range",
        "opportunities",
        "probability >= 0 AND probability <= 100",
    )
    op.create_check_constraint(
        "ck_opportunity_lost_requires_reason",
        "opportunities",
        "current_stage != 'LOST' OR lost_reason_id IS NOT NULL",
    )
    op.create_index(
        "ix_opportunities_scope_stage_created",
        "opportunities",
        ["organization_id", "branch_id", "current_stage", "created_at"],
    )
    op.create_index(
        "ix_opportunities_scope_deleted",
        "opportunities",
        ["organization_id", "branch_id", "deleted_at"],
    )
    op.create_index(
        "ix_followups_status_due",
        "followups",
        ["status", "due_date"],
    )

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            CREATE OR REPLACE FUNCTION prevent_booked_opportunity_update()
            RETURNS trigger AS $$
            BEGIN
                IF OLD.current_stage = 'BOOKED'
                   AND (
                       NEW.current_stage IS DISTINCT FROM OLD.current_stage OR
                       NEW.estimated_value IS DISTINCT FROM OLD.estimated_value OR
                       NEW.probability IS DISTINCT FROM OLD.probability OR
                       NEW.expected_booking_date IS DISTINCT FROM OLD.expected_booking_date OR
                       NEW.lost_reason_id IS DISTINCT FROM OLD.lost_reason_id OR
                       NEW.notes IS DISTINCT FROM OLD.notes OR
                       NEW.deleted_at IS DISTINCT FROM OLD.deleted_at OR
                       NEW.branch_id IS DISTINCT FROM OLD.branch_id OR
                       NEW.family_id IS DISTINCT FROM OLD.family_id OR
                       NEW.assigned_to_user_id IS DISTINCT FROM OLD.assigned_to_user_id OR
                       NEW.opportunity_type IS DISTINCT FROM OLD.opportunity_type
                   )
                THEN
                    RAISE EXCEPTION 'BOOKED opportunities are read-only';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            """
            CREATE TRIGGER trg_prevent_booked_opportunity_update
            BEFORE UPDATE ON opportunities
            FOR EACH ROW
            EXECUTE FUNCTION prevent_booked_opportunity_update();
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS trg_prevent_booked_opportunity_update ON opportunities")
        op.execute("DROP FUNCTION IF EXISTS prevent_booked_opportunity_update")

    op.drop_index("ix_followups_status_due", table_name="followups")
    op.drop_index("ix_opportunities_scope_deleted", table_name="opportunities")
    op.drop_index("ix_opportunities_scope_stage_created", table_name="opportunities")
    op.drop_constraint(
        "ck_opportunity_lost_requires_reason",
        "opportunities",
        type_="check",
    )
    op.drop_constraint(
        "ck_opportunity_probability_range",
        "opportunities",
        type_="check",
    )
