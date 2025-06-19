"""add language to search profile

Revision ID: c9a9121b35fd
Revises: a4b3bb646553
Create Date: 2025-06-19 17:05:53.183784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'c9a9121b35fd'
down_revision: Union[str, None] = 'a4b3bb646553'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'search_profiles',
        sa.Column(
            'language',
            sa.String(2),
            nullable=False,
            server_default='en',
        ),
    )
    op.create_check_constraint(
        'ck_search_profiles_language',
        'search_profiles',
        "language IN ('en','de')",
    )
    op.alter_column('search_profiles', 'language', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_search_profiles_language', 'search_profiles', type_='check')
    op.drop_column('search_profiles', 'language')
