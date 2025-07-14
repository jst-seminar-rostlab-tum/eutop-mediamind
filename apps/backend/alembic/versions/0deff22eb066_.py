"""empty message

Revision ID: 0deff22eb066
Revises: 04bf14d0cb1f, d8c46ac01508
Create Date: 2025-06-23 18:36:41.629533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '0deff22eb066'
down_revision: Union[str, None] = ('04bf14d0cb1f', 'd8c46ac01508')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
