"""merge heads

Revision ID: c7368263114f
Revises: 5a15fbb052d2, e1e416a56286
Create Date: 2025-06-24 19:28:22.623699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'c7368263114f'
down_revision: Union[str, None] = ('5a15fbb052d2', 'e1e416a56286')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
