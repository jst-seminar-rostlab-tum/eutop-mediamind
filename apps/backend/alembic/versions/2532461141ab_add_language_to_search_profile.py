"""add language to search profile

Revision ID: 2532461141ab
Revises: c7507d7a06d7
Create Date: 2025-06-23 21:16:47.619071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '2532461141ab'
down_revision: Union[str, None] = 'c7507d7a06d7'
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
