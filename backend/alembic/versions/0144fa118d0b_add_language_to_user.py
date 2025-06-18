"""add language to user

Revision ID: 0144fa118d0b
Revises: 12eab22fb1be
Create Date: 2025-06-17 23:23:34.181749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '0144fa118d0b'
down_revision: Union[str, None] = '12eab22fb1be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
    op.drop_constraint('ck_users_language', 'users', type_='check')
    op.drop_column('users', 'language')
