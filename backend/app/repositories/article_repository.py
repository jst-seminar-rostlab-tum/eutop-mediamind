from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_session
from sqlalchemy.future import select
from sqlmodel import Session

from app.core.logger import get_logger
from app.models.article import Article

logger = get_logger(__name__)


class ArticleRepository:
    @staticmethod
    async def get_article_by_id(article_id: UUID) -> Article | None:
        async with async_session() as session:
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            return result.scalars().first()

    @staticmethod
    def update_article(session: Session, article: Article) -> Article:
        existing_article = session.get(Article, article.id)
        if existing_article:
            for attr, value in vars(article).items():
                if attr != "_sa_instance_state":
                    setattr(existing_article, attr, value)
            session.commit()
            session.refresh(existing_article)
            return existing_article
        else:
            return None

    @staticmethod
    def insert_articles(articles: list[Article], session) -> list[Article]:
        inserted_articles = []
        for article in articles:
            try:
                session.add(article)
                session.commit()
                session.refresh(article)
                inserted_articles.append(article)
            except IntegrityError as e:
                session.rollback()  # Roll back the failed transaction

                if hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
                    error_detail = str(e.orig)
                    # Check if it's specifically the URL constraint
                    if (
                        "articles_url_key" in error_detail
                        or (
                            "duplicate key value violates unique constraint "
                            '"articles_url_key"'
                        )
                        in error_detail
                    ):
                        logger.warning(
                            f"Article with URL {article.url} already exists, "
                            "skipping."
                        )
                        continue
                    else:
                        # Other unique constraint violation
                        logger.error(f"Unique constraint violation: {e}")
                        continue
                else:
                    # Other integrity error
                    logger.error(f"Failed to insert article: {e}")
                    continue
        return inserted_articles

    @staticmethod
    def get_articles_by_subscription_with_empty_content(
        session, subscription_id: str
    ) -> list[Article]:
        result = session.execute(
            select(Article)
            .where(Article.subscription_id == subscription_id)
            .where(Article.content.is_(None))
        )
        return result.scalars().all()
