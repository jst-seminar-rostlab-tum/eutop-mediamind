"""empty message

Revision ID: 307c2d987d05
Revises: 26554650267f, c6c45b090639
Create Date: 2025-06-27 18:52:38.073338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '307c2d987d05'
down_revision: Union[str, None] = ('26554650267f', 'c6c45b090639')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
