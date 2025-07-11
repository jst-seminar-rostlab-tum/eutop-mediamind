"""Merge heads

Revision ID: f4218eba1395
Revises: 29162befc9ae, 307c2d987d05
Create Date: 2025-06-30 08:54:13.714921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'f4218eba1395'
down_revision: Union[str, None] = ('29162befc9ae', '307c2d987d05')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
