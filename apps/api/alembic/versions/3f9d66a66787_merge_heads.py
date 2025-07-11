"""Merge heads

Revision ID: 3f9d66a66787
Revises: 62043a608597, dcfad6a3ce85
Create Date: 2025-07-01 21:17:20.233946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '3f9d66a66787'
down_revision: Union[str, None] = ('62043a608597', 'dcfad6a3ce85')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
