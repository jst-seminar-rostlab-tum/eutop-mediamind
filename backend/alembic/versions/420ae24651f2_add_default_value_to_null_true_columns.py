"""Add default value to null=true columns
Revision ID: 420ae24651f2
Revises: d72932518738
Create Date: 2025-06-25 19:36:33.800364
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "420ae24651f2"
down_revision: Union[str, None] = "d72932518738"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
