"""add user username

Revision ID: 202606100003
Revises: 202606100002
Create Date: 2026-06-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100003"
down_revision: str | None = "202606100002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=80), nullable=True))
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)
    op.create_index("uq_users_username_lower", "users", [sa.text("lower(username)")], unique=True)

    if op.get_bind().dialect.name == "postgresql":
        op.create_check_constraint(
            "ck_users_username_trimmed",
            "users",
            "username IS NULL OR length(trim(username)) > 0",
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.drop_constraint("ck_users_username_trimmed", "users", type_="check")
    op.drop_index("uq_users_username_lower", table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")
