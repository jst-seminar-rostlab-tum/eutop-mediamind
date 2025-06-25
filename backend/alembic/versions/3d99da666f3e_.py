"""empty message

Revision ID: 3d99da666f3e
Revises: d6de83802d3f, 93c1609bbeb7, 09fa63ba990e
Create Date: 2025-06-25 16:26:11.301091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '3d99da666f3e'
down_revision: Union[str, None] = ('d6de83802d3f', '93c1609bbeb7', '09fa63ba990e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
