"""Merge heads

Revision ID: d50b1d179e6e
Revises: 3d99da666f3e, 420ae24651f2
Create Date: 2025-06-25 20:10:14.779011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'd50b1d179e6e'
down_revision: Union[str, None] = ('3d99da666f3e', '420ae24651f2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
