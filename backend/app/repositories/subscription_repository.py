from uuid import UUID
from app.models.match import Match
from app.models.subscription import Subscription
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import async_session

from app.models.article import Article
from sqlalchemy import select


class SubscriptionRepository:
    @staticmethod
    async def get_all(
        session: AsyncSession,
        search_query: Optional[str] = None
    ) -> list[Subscription]:
        stmt = select(Subscription)
        if search_query:
            stmt = stmt.where(Subscription.name.ilike(f"%{search_query}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_all_no_paywall_with_newsapi_id(
        session: AsyncSession
    ) -> list[Subscription]:
        stmt = select(Subscription).where(
            Subscription.login_works == True,
            Subscription.newsapi_id.isnot(None)
        )
        result = session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def save_article(
        session: AsyncSession,
        subscription: Subscription,
        article: Article
    ) -> None:
        article.subscription_id = subscription.id
        session.add(article)
        session.commit()

    @staticmethod
    async def get_articles_with_empty_content(
        session: AsyncSession
    ) -> dict:
        stmt = (
            select(
                Article.id, Article.url, Subscription.paywall,
                Subscription.config, Subscription.id, Subscription.name
            )
            .join(Subscription, Article.subscription_id == Subscription.id)
            .where(Article.content == None, Article.url.isnot(None))
        )
        result = session.execute(stmt)
        rows = result.all()

        grouped = {}
        for row in rows:
            article_id, url, paywall, config, sub_id, sub_name = row
            key = (sub_id, sub_name)
            if key not in grouped:
                grouped[key] = {
                    "subscription_id": sub_id,
                    "subscription_name": sub_name,
                    "paywall": paywall,
                    "config": config,
                    "content": []
                }
            grouped[key]["content"].append({
                "article_id": article_id,
                "url": url
            })
        return grouped

    @staticmethod
    async def update_article(
        session,
        article: Article
    ) -> Article:
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
