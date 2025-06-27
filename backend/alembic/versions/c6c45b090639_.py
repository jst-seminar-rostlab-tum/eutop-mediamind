"""empty message

Revision ID: c6c45b090639
Revises: 009efbef27ab, 0afdeaced3f3
Create Date: 2025-06-27 16:21:17.381781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'c6c45b090639'
down_revision: Union[str, None] = ('009efbef27ab', '0afdeaced3f3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
