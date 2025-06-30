"""add language to user

Revision ID: c7507d7a06d7
Revises: d627f987e231
Create Date: 2025-06-23 21:15:29.606236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'c7507d7a06d7'
down_revision: Union[str, None] = 'd627f987e231'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1) add language column with default 'en' (backfills existing rows)
    op.add_column(
        'users',
        sa.Column(
            'language',
            sa.String(2),
            nullable=False,
            server_default='en',
        ),
    )
    # 2) add check constraint
    op.create_check_constraint(
        'ck_users_language',
        'users',
        "language IN ('en','de')",
    )
    # 3) remove the server_default so future INSERTs use app default
    op.alter_column('users', 'language', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_users_language', 'users', type_='check')
    op.drop_column('users', 'language')
