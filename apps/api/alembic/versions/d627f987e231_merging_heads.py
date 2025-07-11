"""Merging heads

Revision ID: d627f987e231
Revises: e1e416a56286, 04bf14d0cb1f
Create Date: 2025-06-23 21:14:53.641552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'd627f987e231'
down_revision: Union[str, None] = ('e1e416a56286', '04bf14d0cb1f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
