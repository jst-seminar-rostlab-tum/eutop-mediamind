from uuid import UUID
from typing import List

from sqlalchemy import select, desc
from sqlalchemy.orm.strategy_options import joinedload

from app.models.article import Article
from app.core.db import async_session


class ArticleRepository:
    @staticmethod
    async def get_article_by_id(article_id: UUID) -> Article | None:
        async with async_session() as session:
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            return result.scalars().first()

    @staticmethod
    async def update_article(article: Article) -> Article:
        async with async_session() as session:
            existing_article = await session.get(Article, article.id)
            if existing_article:
                for attr, value in vars(article).items():
                    if attr != "_sa_instance_state":
                        setattr(existing_article, attr, value)
                await session.commit()
                await session.refresh(existing_article)
                return existing_article
            else:
                return None

    @staticmethod
    async def get_sameple_articles(limit: int) -> List[Article]:
        async with async_session() as session:
            result = await session.execute(
                select(Article).order_by(desc(Article.published_at)).limit(limit).options(joinedload('*'))
            )
            return result.unique().scalars().all()
