"""empty message

Revision ID: 09fa63ba990e
Revises: e4f05150f54f, a62d51edab71
Create Date: 2025-06-25 15:43:52.821408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '09fa63ba990e'
down_revision: Union[str, None] = ('e4f05150f54f', 'a62d51edab71')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
