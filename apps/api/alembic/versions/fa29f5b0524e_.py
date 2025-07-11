"""empty message

Revision ID: fa29f5b0524e
Revises: 3d99da666f3e, 2532461141ab
Create Date: 2025-06-25 19:14:29.302835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'fa29f5b0524e'
down_revision: Union[str, None] = ('3d99da666f3e', '2532461141ab')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
