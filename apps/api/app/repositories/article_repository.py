import uuid
from datetime import date, datetime
from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.core.logger import get_logger
from app.models.article import Article, ArticleStatus
from app.models.match import Match
from app.repositories.matching_run_repository import MatchingRunRepository
from app.repositories.subscription_repository import SubscriptionRepository

logger = get_logger(__name__)


class ArticleRepository:
    """Repository for managing Article entities in the database."""

    @staticmethod
    async def get_article_by_id(article_id: UUID) -> Optional[Article]:
        """
        Retrieve a single Article by its UUID.
        Returns None if no article is found.
        """

        async with async_session() as session:
            statement = select(Article).where(Article.id == article_id)
            article: Optional[Article] = (
                await session.execute(statement)
            ).scalar_one_or_none()
            return article

    @staticmethod
    async def update_article(article: Article) -> Optional[Article]:
        """
        Update an existing Article in the database.
        Returns the updated Article, or None if it does not exist.
        """
        async with async_session() as session:
            existing_article = await session.get(Article, article.id)
            if not existing_article:
                return None

            existing_article_without_id = article.model_dump(
                exclude_unset=True, exclude={"id"}
            )
            for key, val in existing_article_without_id.items():
                setattr(existing_article, key, val)

            session.add(existing_article)
            await session.commit()
            await session.refresh(existing_article)
            return existing_article

    @staticmethod
    async def update_article_summary(
        article_id: UUID, article_summary: str
    ) -> Optional[Article]:
        """
        Update only the 'summary' field of an existing Article.
        Returns the updated Article, or None if it does not exist.
        """
        async with async_session() as session:
            existing_article = await session.get(Article, article_id)
            if not existing_article:
                return None

            existing_article.summary = article_summary
            existing_article.status = ArticleStatus.SUMMARIZED
            session.add(existing_article)
            await session.commit()
            await session.refresh(existing_article)
            return existing_article

    @staticmethod
    async def create_article(article: Article, logger=logger) -> Article:
        """
        Add a new Article to the database.
        """
        async with async_session() as session:
            try:
                session.add(article)
                await session.commit()
                await session.refresh(article)
                return article
            except IntegrityError as e:
                await session.rollback()
                if hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
                    error_detail = str(e.orig)
                    # Check if it's specifically the URL constraint
                    if (
                        "duplicate key value violates unique "
                        'constraint "articles_url_key"' in error_detail
                    ):
                        logger.warning(
                            f"Article with URL {article.url} "
                            "already exists, skipping."
                        )
                        return
                logger.error(f"Failed to insert article: {e}")
                return
            except Exception as e:
                logger.error(f"Failed to insert article {article.url}: {e}")
                await session.rollback()
                return

    @staticmethod
    async def create_articles_batch(
        articles: list[Article], batch_size: int = 50, logger=logger
    ):
        successful = []
        async with async_session() as session:
            for i in range(0, len(articles), batch_size):
                batch = articles[i : i + batch_size]
                try:
                    session.add_all(batch)
                    await session.commit()
                    successful.extend(batch)
                except Exception:
                    await session.rollback()
                    logger.warning("Batch failed, inserting individual now")

                    # Try inserting articles one-by-one
                    for article in batch:
                        created_article = (
                            await ArticleRepository.create_article(
                                article, logger=logger
                            )
                        )
                        if created_article:
                            successful.append(created_article)
            logger.info(f"Inserted {len(successful)} articles successfully.")
        return successful

    @staticmethod
    async def list_articles(
        limit: int = 100, offset: int = 0, set_of: int = 0
    ) -> Sequence[Article]:
        """
        List articles with optional pagination and batch processing.
        """
        async with async_session() as session:
            statement = (
                select(Article).limit(limit).offset(offset + (set_of * limit))
            )
            articles: list[Article] = (
                (await session.execute(statement)).scalars().all()
            )
            return articles

    @staticmethod
    async def list_articles_without_summary(
        limit: int = 100,
        datetime_start: datetime = datetime.combine(
            date.today(), datetime.min.time()
        ),
        datetime_end: datetime = datetime.now(),
    ) -> Sequence[Article]:
        """
        List articles that have no summary yet, with pagination.
        """
        async with async_session() as session:
            statement = (
                select(Article)
                .where(
                    Article.status == "SCRAPED",
                    Article.published_at.between(datetime_start, datetime_end),
                    or_(Article.summary.is_(None), Article.summary == ""),
                )
                .limit(limit)
            )
            unsummarized_articles: Sequence[Article] = (
                (await session.execute(statement)).scalars().all()
            )

            return unsummarized_articles

    @staticmethod
    async def list_articles_with_summary(
        limit: int = 100,
        date_start: date = date.today(),
        date_end: date = date.today(),
    ) -> List[Article]:
        """
        List articles that have a summary, with pagination.
        """
        async with async_session() as session:
            statement = (
                select(Article)
                .where(
                    Article.summary.isnot(None),
                    Article.summary != "",
                    Article.status == "TRANSLATED",
                    Article.published_at.between(date_start, date_end),
                )
                .limit(limit)
            )

            summarized_articles: List[Article] = (
                (await session.execute(statement)).scalars().all()
            )

            return summarized_articles

    @staticmethod
    async def get_matched_articles_for_profile_for_create_pdf(
        search_profile_id: uuid.UUID,
        limit: int = 100,
    ) -> List[Article]:
        async with async_session() as session:
            last_matching_run = (
                await MatchingRunRepository.get_last_matching_run(session)
            )

            if not last_matching_run:
                return []

            # Get subscription IDs that are linked to the search profile
            subscriptions_data = await SubscriptionRepository.\
                get_all_subscriptions_with_search_profile(
                search_profile_id
            )
            # Filter to get only subscribed subscription IDs
            linked_subscription_ids = [
                sub.id for sub in subscriptions_data if sub.is_subscribed
            ]

            query = (
                select(Match)
                .options(
                    selectinload(Match.article).selectinload(
                        Article.subscription
                    ),
                    selectinload(Match.article).selectinload(Article.keywords),
                )
                .where(
                    Match.matching_run_id == last_matching_run.id,
                    Match.search_profile_id == search_profile_id,
                )
                .order_by(Match.sorting_order.asc())
                .limit(limit)
            )
            matches = (await session.execute(query)).scalars().all()

            # Process articles to modify content for non-subscribed articles
            articles = []
            for match in matches:
                if match.article is not None:
                    article = match.article
                    # If article's subscription is not 
                    # linked to the search profile, modify content
                    if article.subscription_id not in linked_subscription_ids:
                        article.content_en = "Subscribe to unlock the article"
                        article.content_de = "Abonnieren Sie, " \
                        "um den Artikel freizuschalten"
                    articles.append(article)

            return articles

    @staticmethod
    async def list_new_articles_by_subscription(
        subscription_id: UUID,
    ) -> List[Article]:
        """
        List all articles with status 'NEW' and the given subscription_id.
        """
        async with async_session() as session:
            statement = select(Article).where(
                Article.status == "NEW",
                Article.subscription_id == subscription_id,
            )
            articles: Sequence[Article] = (
                (await session.execute(statement)).scalars().all()
            )
            return articles

    @staticmethod
    async def get_articles_without_translations(
        limit: int = 100,
        datetime_start: datetime = datetime.combine(
            date.today(), datetime.min.time()
        ),
        datetime_end: datetime = datetime.now(),
    ) -> Sequence[Article]:
        """
        Returns articles that are missing at least one translation
        (title_en, title_de, content_en, content_de, summary_en, summary_de).
        """
        async with async_session() as session:
            statement = (
                select(Article)
                .where(
                    Article.status == "SUMMARIZED",
                    Article.published_at.between(datetime_start, datetime_end),
                    or_(
                        Article.title_en.is_(None),
                        Article.title_en == "",
                        Article.title_de.is_(None),
                        Article.title_de == "",
                        Article.content_en.is_(None),
                        Article.content_en == "",
                        Article.content_de.is_(None),
                        Article.content_de == "",
                        Article.summary_en.is_(None),
                        Article.summary_en == "",
                        Article.summary_de.is_(None),
                        Article.summary_de == "",
                    ),
                )
                .limit(limit)
            )
            articles_missing_translations: Sequence[Article] = (
                (await session.execute(statement)).scalars().all()
            )

            return articles_missing_translations

    @staticmethod
    async def update_translations(
        article_id: UUID,
        title_en: Optional[str] = None,
        title_de: Optional[str] = None,
        content_en: Optional[str] = None,
        content_de: Optional[str] = None,
        summary_en: Optional[str] = None,
        summary_de: Optional[str] = None,
    ) -> Optional[Article]:
        """
        Update translation fields of an existing Article.
        """
        async with async_session() as session:
            existing_article = await session.get(Article, article_id)
            if not existing_article:
                return None

            if title_en is not None:
                existing_article.title_en = title_en
            if title_de is not None:
                existing_article.title_de = title_de
            if content_en is not None:
                existing_article.content_en = content_en
            if content_de is not None:
                existing_article.content_de = content_de
            if summary_en is not None:
                existing_article.summary_en = summary_en
            if summary_de is not None:
                existing_article.summary_de = summary_de

            existing_article.status = ArticleStatus.TRANSLATED

            session.add(existing_article)
            await session.commit()
            await session.refresh(existing_article)
            return existing_article

    @staticmethod
    # get subscription id for an article
    async def get_subscription_id_for_article(
        article_id: UUID,
    ) -> Optional[UUID]:
        """
        Retrieve the subscription ID for a given article.
        Returns None if the article does not have a subscription.
        """
        async with async_session() as session:
            statement = select(Article).where(Article.id == article_id)
            article: Optional[Article] = (
                await session.execute(statement)
            ).scalar_one_or_none()
            return article.subscription_id if article else None
