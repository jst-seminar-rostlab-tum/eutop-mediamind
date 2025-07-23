"""empty message

Revision ID: efd92ff0b2df
Revises: 46186a3583c9, e7b0b013f9db
Create Date: 2025-07-05 12:48:03.523807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'efd92ff0b2df'
down_revision: Union[str, None] = ('46186a3583c9', 'e7b0b013f9db')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
