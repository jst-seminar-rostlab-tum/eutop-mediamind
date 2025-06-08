from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_session
from sqlalchemy.future import select

from app.models.article import Article
from app.models.match import Match
from app.models.subscription import Subscription


class SubscriptionRepository:
    @staticmethod
    async def get_all(
        session: AsyncSession, search_query: Optional[str] = None
    ) -> list[Subscription]:
        stmt = select(Subscription)
        if search_query:
            stmt = stmt.where(Subscription.name.ilike(f"%{search_query}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_all_no_paywall_with_newsapi_id(
        session: AsyncSession, uuid: str = None
    ) -> list[Subscription]:
        stmt = select(Subscription).where(
            Subscription.login_works == True,
            Subscription.newsapi_id.isnot(None),
        )

        if uuid is not None:
            stmt = stmt.where(Subscription.id == uuid)

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def save_article(
        session: AsyncSession, subscription: Subscription, article: Article
    ) -> None:
        article.subscription_id = subscription.id
        session.add(article)
        try:
            await session.commit()
        except IntegrityError as e:
            if (
                'duplicate key value violates unique constraint "articles_url_key"'
                in str(e)
            ):
                await session.rollback()
            else:
                raise

    @staticmethod
    async def get_articles_with_empty_content(session: AsyncSession) -> list:
        stmt = (
            select(
                Article.id,
                Article.url,
                Subscription.paywall,
                Subscription.config,
                Subscription.id,
                Subscription.name,
                Subscription.domain,
            )
            .join(Subscription, Article.subscription_id == Subscription.id)
            .where(Article.content == None, Article.url.isnot(None))
        )
        result = await session.execute(stmt)
        rows = result.all()

        grouped = []
        seen = {}

        for row in rows:
            article_id, url, paywall, config, sub_id, sub_name, sub_domain = (
                row
            )
            if sub_id not in seen:
                group = {
                    "subscription_id": sub_id,
                    "subscription_name": sub_name,
                    "paywall": paywall,
                    "config": config,
                    "content": [],
                    "domain": sub_domain,
                }
                grouped.append(group)
                seen[sub_id] = group
            seen[sub_id]["content"].append(
                {"article_id": article_id, "url": url}
            )

        return grouped

    @staticmethod
    async def update_article(
        session: AsyncSession, article: Article
    ) -> Article | None:
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
    async def get_articles_with_empty_content_for_subscription(
        session: AsyncSession, subscription_id: str
    ) -> dict | None:
        stmt = (
            select(
                Article.id,
                Article.url,
                Subscription.paywall,
                Subscription.config,
                Subscription.id,
                Subscription.name,
                Subscription.domain,
            )
            .join(Subscription, Article.subscription_id == Subscription.id)
            .where(
                Article.content == None,
                Article.url.isnot(None),
                Subscription.id == subscription_id,
            )
        )
        result = await session.execute(stmt)
        rows = result.all()

        if not rows:
            return None

        # Since we're filtering by a single subscription, we expect one group
        group = {
            "subscription_id": subscription_id,
            "subscription_name": rows[0][5],
            "paywall": rows[0][2],
            "config": rows[0][3],
            "content": [],
            "domain": rows[0][6],
        }

        for row in rows:
            article_id, url = row[0], row[1]
            group["content"].append({"article_id": article_id, "url": url})

        return [group]

    @staticmethod
    def get_subscription_by_id(
        session, subscription_id: str
    ) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.id == subscription_id)
        result = session.execute(stmt)
        return result.scalars().first()
