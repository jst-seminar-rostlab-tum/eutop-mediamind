"""Add default value to null=true columns

Revision ID: 420ae24651f2
Revises: d72932518738
Create Date: 2025-06-25 19:36:33.800364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '420ae24651f2'
down_revision: Union[str, None] = 'd72932518738'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'entities', 'id',
        server_default=sa.text("'00000000-0000-0000-0000-000000000000'")
    )
    op.alter_column(
        'entities', 'entity_type',
        server_default=sa.text("'unknown'")
    )
    op.alter_column(
        'entities', 'value',
        server_default=sa.text("'unknown'")
    )
    op.alter_column(
        'entities', 'article_id',
        server_default=sa.text("'00000000-0000-0000-0000-000000000000'")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'entities', 'id',
        server_default=None
    )
    op.alter_column(
        'entities', 'entity_type',
        server_default=None
    )
    op.alter_column(
        'entities', 'value',
        server_default=None
    )
    op.alter_column(
        'entities', 'article_id',
        server_default=None
    )
