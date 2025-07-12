"""empty message

Revision ID: 819c8c6698fd
Revises: 105a3eb259e5, 36d16a1fbaec, b947a2c9659d
Create Date: 2025-07-12 13:20:16.692242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '819c8c6698fd'
down_revision: Union[str, None] = ('105a3eb259e5', '36d16a1fbaec', 'b947a2c9659d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
