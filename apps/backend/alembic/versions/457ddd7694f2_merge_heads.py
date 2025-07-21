"""Merge heads

Revision ID: 457ddd7694f2
Revises: 0c826f19ce87, 6ab7103717b1
Create Date: 2025-07-21 18:01:43.199488

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '457ddd7694f2'
down_revision: Union[str, None] = ('0c826f19ce87', '6ab7103717b1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
