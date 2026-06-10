"""create gallery upgrade requests

Revision ID: 202606100011
Revises: 202606100010
Create Date: 2026-06-10 01:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100011"
down_revision: str | None = "202606100010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gallery_upgrade_requests",
        sa.Column("gallery_id", sa.Uuid(), nullable=False),
        sa.Column("current_limit", sa.Integer(), nullable=False),
        sa.Column("requested_limit", sa.Integer(), nullable=False),
        sa.Column("additional_photos", sa.Integer(), nullable=False),
        sa.Column("price_per_photo", sa.Integer(), nullable=False),
        sa.Column("total_amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["gallery_id"], ["galleries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gallery_upgrade_requests_gallery_id", "gallery_upgrade_requests", ["gallery_id"])


def downgrade() -> None:
    op.drop_index("ix_gallery_upgrade_requests_gallery_id", table_name="gallery_upgrade_requests")
    op.drop_table("gallery_upgrade_requests")
