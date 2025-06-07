from uuid import UUID

from sqlalchemy.ext.asyncio import async_session
from sqlalchemy.future import select

from app.models.article import Article


class ArticleRepository:
    @staticmethod
    async def get_article_by_id(article_id: UUID) -> Article | None:
        async with async_session() as session:
            article = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            return article.scalars().first()

    @staticmethod
    async def update_article(article: Article) -> Article | None:
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
