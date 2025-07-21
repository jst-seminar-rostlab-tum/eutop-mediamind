"""Merge heads

Revision ID: a5e9a3eb2301
Revises: 457ddd7694f2, db3d4934b5cf
Create Date: 2025-07-21 18:35:07.492658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'a5e9a3eb2301'
down_revision: Union[str, None] = ('457ddd7694f2', 'db3d4934b5cf')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
