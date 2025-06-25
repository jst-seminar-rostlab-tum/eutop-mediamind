"""merge heads

Revision ID: a62d51edab71
Revises: c7368263114f, 369e76412515
Create Date: 2025-06-24 19:28:52.094592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'a62d51edab71'
down_revision: Union[str, None] = ('c7368263114f', '369e76412515')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
