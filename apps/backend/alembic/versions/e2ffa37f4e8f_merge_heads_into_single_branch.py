"""merge heads into single branch

Revision ID: e2ffa37f4e8f
Revises: 04bf14d0cb1f, d8c46ac01508
Create Date: 2025-06-24 20:38:53.823653

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "e2ffa37f4e8f"
down_revision: Union[str, None] = ("04bf14d0cb1f", "d8c46ac01508")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
