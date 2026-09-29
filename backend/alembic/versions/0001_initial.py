"""Single Alembic head: initial schema for users/projects/stories/contact."""
from __future__ import annotations

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    from alembic import op
    import sqlalchemy as sa

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_id", "users", ["id"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_id", "projects", ["id"])

    op.create_table(
        "stories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stories_id", "stories", ["id"])

    op.create_table(
        "contact_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contact_messages_id", "contact_messages", ["id"])
    op.create_index("ix_contact_messages_email", "contact_messages", ["email"])


def downgrade() -> None:
    from alembic import op

    op.drop_index("ix_contact_messages_email", table_name="contact_messages")
    op.drop_index("ix_contact_messages_id", table_name="contact_messages")
    op.drop_table("contact_messages")
    op.drop_index("ix_stories_id", table_name="stories")
    op.drop_table("stories")
    op.drop_index("ix_projects_id", table_name="projects")
    op.drop_table("projects")
    op.drop_table("users")
