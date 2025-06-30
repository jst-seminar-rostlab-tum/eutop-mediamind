"""Merge heads

Revision ID: 29162befc9ae
Revises: 3e8a9b88e46c, 4457e8b43ae3
Create Date: 2025-06-27 12:57:35.114415

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "29162befc9ae"
down_revision: Union[str, None] = ("3e8a9b88e46c", "4457e8b43ae3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
