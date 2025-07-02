"""empty message

Revision ID: 108b44256ce2
Revises: 7b0a19c21990, 87f11d9a7418
Create Date: 2025-07-02 15:45:32.284412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '108b44256ce2'
down_revision: Union[str, None] = ('7b0a19c21990', '87f11d9a7418')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
