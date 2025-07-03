"""Merge heads

Revision ID: 7b0a19c21990
Revises: 3f9d66a66787, 59e17a067fe2
Create Date: 2025-07-02 12:43:30.368491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '7b0a19c21990'
down_revision: Union[str, None] = ('3f9d66a66787', '59e17a067fe2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
