"""create gallery management

Revision ID: 202606100009
Revises: 202606100008
Create Date: 2026-06-10 00:09:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100009"
down_revision: str | None = "202606100008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "galleries",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("booking_item_id", sa.Uuid(), nullable=False),
        sa.Column("gallery_name", sa.String(length=160), nullable=False),
        sa.Column("gallery_status", sa.String(length=40), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["booking_item_id"], ["booking_items.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_gallery_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_item_id", name="uq_gallery_booking_item"),
    )
    op.create_index("ix_galleries_branch_id", "galleries", ["branch_id"])
    op.create_index("ix_galleries_booking_id", "galleries", ["booking_id"])
    op.create_index("ix_galleries_booking_item_id", "galleries", ["booking_item_id"])
    op.create_index("ix_galleries_gallery_status", "galleries", ["gallery_status"])

    op.create_table(
        "gallery_photos",
        sa.Column("gallery_id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("thumbnail_path", sa.Text(), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("image_width", sa.Integer(), nullable=False),
        sa.Column("image_height", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("file_size >= 0", name="ck_gallery_photo_file_size_non_negative"),
        sa.CheckConstraint("image_width > 0", name="ck_gallery_photo_width_positive"),
        sa.CheckConstraint("image_height > 0", name="ck_gallery_photo_height_positive"),
        sa.ForeignKeyConstraint(["gallery_id"], ["galleries.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("gallery_id", "storage_path", name="uq_gallery_photo_storage_path"),
    )
    op.create_index("ix_gallery_photos_gallery_id", "gallery_photos", ["gallery_id"])

    op.create_table(
        "favorite_selections",
        sa.Column("gallery_id", sa.Uuid(), nullable=False),
        sa.Column("gallery_photo_id", sa.Uuid(), nullable=False),
        sa.Column("selected_by_name", sa.String(length=160), nullable=False),
        sa.Column("selected_by_email", sa.String(length=255), nullable=True),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["gallery_id"], ["galleries.id"]),
        sa.ForeignKeyConstraint(["gallery_photo_id"], ["gallery_photos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "gallery_id",
            "gallery_photo_id",
            "selected_by_email",
            name="uq_favorite_gallery_photo_email",
        ),
    )
    op.create_index("ix_favorite_selections_gallery_id", "favorite_selections", ["gallery_id"])
    op.create_index(
        "ix_favorite_selections_gallery_photo_id",
        "favorite_selections",
        ["gallery_photo_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_favorite_selections_gallery_photo_id", table_name="favorite_selections")
    op.drop_index("ix_favorite_selections_gallery_id", table_name="favorite_selections")
    op.drop_table("favorite_selections")
    op.drop_index("ix_gallery_photos_gallery_id", table_name="gallery_photos")
    op.drop_table("gallery_photos")
    op.drop_index("ix_galleries_gallery_status", table_name="galleries")
    op.drop_index("ix_galleries_booking_item_id", table_name="galleries")
    op.drop_index("ix_galleries_booking_id", table_name="galleries")
    op.drop_index("ix_galleries_branch_id", table_name="galleries")
    op.drop_table("galleries")
