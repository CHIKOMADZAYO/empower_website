"""Constrain user roles to the supported RBAC roles."""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "3c71e4a92f10"
down_revision: str | None = "b7f3a8d9210c"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    users = sa.Table(
        "users",
        sa.MetaData(),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.Index("ix_users_id", "id"),
        sa.Index("ix_users_username", "username", unique=True),
    )
    with op.batch_alter_table("users", copy_from=users) as batch_op:
        batch_op.create_check_constraint(
            "user_role",
            "role IN ('admin', 'editor', 'viewer')",
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("user_role", type_="check")
