"""Merged clean up email table and merg repot and json format

Revision ID: e4f05150f54f
Revises: 369e76412515, 5a15fbb052d2
Create Date: 2025-06-25 15:25:37.507238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'e4f05150f54f'
down_revision: Union[str, None] = ('369e76412515', '5a15fbb052d2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
