"""Constrain user roles to the supported RBAC roles."""

from __future__ import annotations

revision = "0002_constrain_user_roles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from alembic import op

    with op.batch_alter_table("users") as batch_op:
        batch_op.create_check_constraint(
            "user_role",
            "role IN ('admin', 'editor', 'viewer')",
        )


def downgrade() -> None:
    from alembic import op

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("user_role", type_="check")