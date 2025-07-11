"""added new status enums

Revision ID: 62043a608597
Revises: f4218eba1395
Create Date: 2025-06-30 15:13:19.232245

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "62043a608597"
down_revision: Union[str, None] = "f4218eba1395"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new enum values to the existing articlestatus enum
    op.execute("ALTER TYPE articlestatus ADD VALUE IF NOT EXISTS 'SUMMARIZED'")
    op.execute("ALTER TYPE articlestatus ADD VALUE IF NOT EXISTS 'TRANSLATED'")
    op.execute("ALTER TYPE articlestatus ADD VALUE IF NOT EXISTS 'EMBEDDED'")


def downgrade() -> None:
    """Downgrade schema."""
    # Note: PostgreSQL doesn't support removing enum values directly
    # You would need to recreate the enum type if you want to remove values
    # This is a simplified downgrade that doesn't actually remove the enum values
    pass
