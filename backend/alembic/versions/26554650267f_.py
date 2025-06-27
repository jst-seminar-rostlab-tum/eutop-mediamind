"""empty message

Revision ID: 26554650267f
Revises: 37080347559f, fa29f5b0524e
Create Date: 2025-06-25 23:37:17.459645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '26554650267f'
down_revision: Union[str, None] = ('37080347559f', 'fa29f5b0524e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
