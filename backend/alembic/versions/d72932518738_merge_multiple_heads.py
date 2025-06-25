"""Merge multiple heads

Revision ID: d72932518738
Revises: 369e76412515, 5a15fbb052d2, bdee7e922ed6
Create Date: 2025-06-24 22:19:54.938901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'd72932518738'
down_revision: Union[str, None] = ('369e76412515', '5a15fbb052d2', 'bdee7e922ed6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
