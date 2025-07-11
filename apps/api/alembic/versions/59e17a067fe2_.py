"""empty message

Revision ID: 59e17a067fe2
Revises: 2a622949461f, 62043a608597
Create Date: 2025-07-01 22:05:07.962123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '59e17a067fe2'
down_revision: Union[str, None] = ('2a622949461f', '62043a608597')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
