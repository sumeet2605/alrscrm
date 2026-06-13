"""add opportunity package

Revision ID: 202606100020
Revises: 202606100019
Create Date: 2026-06-12 00:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100020"
down_revision: str | None = "202606100019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("opportunities", sa.Column("package_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_opportunity_package",
        "opportunities",
        "packages",
        ["package_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_opportunity_package", "opportunities", type_="foreignkey")
    op.drop_column("opportunities", "package_id")
