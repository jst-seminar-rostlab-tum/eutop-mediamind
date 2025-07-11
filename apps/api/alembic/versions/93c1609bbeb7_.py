"""empty message

Revision ID: 93c1609bbeb7
Revises: d8c46ac01508, 837e0cff8ba7, 04bf14d0cb1f
Create Date: 2025-06-25 11:09:59.672863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '93c1609bbeb7'
down_revision: Union[str, None] = ('d8c46ac01508', '04bf14d0cb1f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
