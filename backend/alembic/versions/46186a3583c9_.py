"""empty message

Revision ID: 46186a3583c9
Revises: 108b44256ce2, 92673c837211
Create Date: 2025-07-03 17:10:12.094314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '46186a3583c9'
down_revision: Union[str, None] = ('108b44256ce2', '92673c837211')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
