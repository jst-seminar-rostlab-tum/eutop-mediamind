"""empty message

Revision ID: 3e8a9b88e46c
Revises: 37080347559f, d50b1d179e6e
Create Date: 2025-06-26 13:07:20.259865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '3e8a9b88e46c'
down_revision: Union[str, None] = ('37080347559f', 'd50b1d179e6e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
