"""Merge heads

Revision ID: 37080347559f
Revises: 3d99da666f3e, d72932518738
Create Date: 2025-06-25 21:24:31.873157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '37080347559f'
down_revision: Union[str, None] = ('3d99da666f3e', 'd72932518738')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
