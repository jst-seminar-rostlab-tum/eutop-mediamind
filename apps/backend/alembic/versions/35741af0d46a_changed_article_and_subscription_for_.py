"""changed article and subscription for crawling and scraping

Revision ID: 35741af0d46a
Revises: cce014679366
Create Date: 2025-06-11 14:37:21.895059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '35741af0d46a'
down_revision: Union[str, None] = 'cce014679366'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    articlestatus_enum = sa.Enum('NEW', 'SCRAPED', 'ERROR', name='articlestatus')
    articlestatus_enum.create(op.get_bind())

    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('status', articlestatus_enum, nullable=False, server_default="SCRAPED"))
    op.add_column('articles', sa.Column('crawled_at', sa.DateTime(), nullable=False))
    op.add_column('articles', sa.Column('scraped_at', sa.DateTime(), nullable=True))
    op.alter_column('articles', 'content',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('articles', 'author',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('articles', 'language',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('articles', 'category',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_unique_constraint(None, 'articles', ['url'])
    op.add_column('subscriptions', sa.Column('paywall', sa.Boolean(), nullable=False))
    op.add_column('subscriptions', sa.Column('login_works', sa.Boolean(), nullable=False))
    op.add_column('subscriptions', sa.Column('newsapi_id', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.add_column('subscriptions', sa.Column('vault_path', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.alter_column(
        'subscriptions',
        'config',
        existing_type=sa.VARCHAR(length=255),
        type_=sa.JSON(),
        postgresql_using="config::json",
        nullable=True
    )
    op.alter_column('subscriptions', 'scraper_type',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.create_unique_constraint(None, 'subscriptions', ['name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'subscriptions', type_='unique')
    op.alter_column('subscriptions', 'scraper_type',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column(
        'subscriptions',
        'config',
        existing_type=sa.JSON(),
        type_=sa.VARCHAR(length=255),
        nullable=False,
        postgresql_using="config::text"
    )
    op.drop_column('subscriptions', 'vault_path')
    op.drop_column('subscriptions', 'newsapi_id')
    op.drop_column('subscriptions', 'login_works')
    op.drop_column('subscriptions', 'paywall')
    op.drop_constraint(None, 'articles', type_='unique')
    op.alter_column('articles', 'category',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('articles', 'language',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('articles', 'author',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('articles', 'content',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('articles', 'scraped_at')
    op.drop_column('articles', 'crawled_at')
    op.drop_column('articles', 'status')
    # ### end Alembic commands ###
