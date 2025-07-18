"""add matching_run

Revision ID: 2a622949461f
Revises: f4218eba1395
Create Date: 2025-07-01 11:59:59.271915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '2a622949461f'
down_revision: Union[str, None] = 'f4218eba1395'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('matching_runs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('algorithm_version', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('matches', sa.Column('matching_run_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_matches_matching_run_id'), 'matches', ['matching_run_id'], unique=False)
    op.create_foreign_key(None, 'matches', 'matching_runs', ['matching_run_id'], ['id'])
    op.add_column('reports', sa.Column('matching_run_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'reports', 'matching_runs', ['matching_run_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'reports', type_='foreignkey')
    op.drop_column('reports', 'matching_run_id')
    op.drop_constraint(None, 'matches', type_='foreignkey')
    op.drop_index(op.f('ix_matches_matching_run_id'), table_name='matches')
    op.drop_column('matches', 'matching_run_id')
    op.drop_table('matching_runs')
    # ### end Alembic commands ###
