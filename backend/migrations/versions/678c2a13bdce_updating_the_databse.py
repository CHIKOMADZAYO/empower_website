"""Updating the Databse

Revision ID: 678c2a13bdce
Revises: 3c71e4a92f10
Create Date: 2026-10-01 23:08:24.123639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '678c2a13bdce'
down_revision: Union[str, Sequence[str], None] = '3c71e4a92f10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The preceding revisions already create the base schema and activity logs.
    # This revision only adds the project image URL introduced by the model.
    op.add_column("projects", sa.Column("image_url", sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("projects", "image_url")
