"""empty message

Revision ID: 87f11d9a7418
Revises: 59e17a067fe2, d445a6780cc4
Create Date: 2025-07-02 11:21:44.096009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '87f11d9a7418'
down_revision: Union[str, None] = ('59e17a067fe2', 'd445a6780cc4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
