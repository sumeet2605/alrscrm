"""production readiness

Revision ID: 202606100019
Revises: 202606100018
Create Date: 2026-06-11 00:19:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202606100019"
down_revision: str | None = "202606100018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _uuid_type():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.UUID(as_uuid=True)
    return sa.String(length=36)


def upgrade() -> None:
    op.create_table(
        "backup_configurations",
        sa.Column("backup_enabled", sa.Boolean(), nullable=False),
        sa.Column("backup_frequency", sa.String(length=40), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("last_backup_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", _uuid_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("retention_days > 0", name="ck_backup_retention_positive"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("backup_configurations")
