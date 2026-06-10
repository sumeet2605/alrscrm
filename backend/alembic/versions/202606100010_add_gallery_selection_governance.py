"""add gallery selection governance

Revision ID: 202606100010
Revises: 202606100009
Create Date: 2026-06-10 00:50:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100010"
down_revision: str | None = "202606100009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "galleries",
        sa.Column("selection_limit", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "galleries",
        sa.Column("selection_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "galleries",
        sa.Column("selection_submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "galleries",
        sa.Column(
            "selection_locked", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )
    op.add_column(
        "galleries",
        sa.Column("selection_deadline", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "galleries",
        sa.Column("allow_download", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "galleries",
        sa.Column("allow_watermark", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "galleries",
        sa.Column("reopen_count", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("galleries", "reopen_count")
    op.drop_column("galleries", "allow_watermark")
    op.drop_column("galleries", "allow_download")
    op.drop_column("galleries", "selection_deadline")
    op.drop_column("galleries", "selection_locked")
    op.drop_column("galleries", "selection_submitted_at")
    op.drop_column("galleries", "selection_count")
    op.drop_column("galleries", "selection_limit")
