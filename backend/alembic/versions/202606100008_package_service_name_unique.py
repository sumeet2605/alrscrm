"""use service type in package uniqueness

Revision ID: 202606100008
Revises: 202606100007
Create Date: 2026-06-10 00:08:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "202606100008"
down_revision: str | None = "202606100007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("uq_package_branch_name", "packages", type_="unique")
    op.create_unique_constraint(
        "uq_package_branch_service_name", "packages", ["branch_id", "service_type", "name"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_package_branch_service_name", "packages", type_="unique")
    op.create_unique_constraint("uq_package_branch_name", "packages", ["branch_id", "name"])
