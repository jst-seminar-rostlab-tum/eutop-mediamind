"""Add EMPTY status to report

Revision ID: 0c826f19ce87
Revises: 3fe6a8f53543
Create Date: 2025-07-20 20:41:59.721721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '0c826f19ce87'
down_revision: Union[str, None] = '3fe6a8f53543'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE reportstatus ADD VALUE 'EMPTY'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
# Apparently you cannot delete enum values in PostgreSQL
