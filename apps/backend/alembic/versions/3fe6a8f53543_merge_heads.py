"""merge heads

Revision ID: 3fe6a8f53543
Revises: 007a6a6e7acd, de3c17bebf87
Create Date: 2025-07-17 23:47:31.088486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '3fe6a8f53543'
down_revision: Union[str, None] = ('007a6a6e7acd', 'de3c17bebf87')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
