from typing import List
from uuid import UUID

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.db import async_session
from app.models import Article, Subscription
from app.models.associations import SearchProfileSubscriptionLink
from app.schemas.subscription_schemas import (
    SubscriptionRead,
    SubscriptionSummary,
)
from app.services.web_harvester.crawler import CrawlerType, get_crawlers
from app.services.web_harvester.scraper import get_scraper


class SubscriptionRepository:
    @staticmethod
    async def get_all_subscriptions_with_search_profile(
        search_profile_id: UUID,
    ) -> List[SubscriptionSummary]:
        async with async_session() as session:
            # Alias to improve readability (optional)
            spsl = aliased(SearchProfileSubscriptionLink)

            # Query subscriptions and whether they are linked
            # to the given search profile
            stmt = select(
                Subscription.id,
                Subscription.name,
                exists()
                .where(
                    (spsl.search_profile_id == search_profile_id)
                    & (spsl.subscription_id == Subscription.id)
                )
                .label("is_subscribed"),
            )

            result = await session.execute(stmt)

            return [
                SubscriptionSummary(
                    id=row.id, name=row.name, is_subscribed=row.is_subscribed
                )
                for row in result
            ]

    @staticmethod
    async def get_all() -> list[SubscriptionSummary]:
        async with async_session() as session:
            stmt = select(Subscription.id, Subscription.name)
            result = await session.execute(stmt)

            return [
                SubscriptionSummary(
                    id=row.id, name=row.name, is_subscribed=False
                )
                for row in result
            ]

    @staticmethod
    async def set_subscriptions_for_profile(
        profile_id: UUID, subscriptions: list[SubscriptionSummary], session
    ) -> None:
        await session.execute(
            delete(SearchProfileSubscriptionLink).where(
                SearchProfileSubscriptionLink.search_profile_id == profile_id
            )
        )

        subscribed = [s for s in subscriptions if s.is_subscribed]

        new_links = [
            SearchProfileSubscriptionLink(
                search_profile_id=profile_id,
                subscription_id=s.id,
            )
            for s in subscribed
        ]

        session.add_all(new_links)

    @staticmethod
    async def get_by_id(session, subscription_id: UUID) -> Subscription | None:
        return await session.get(Subscription, subscription_id)

    @staticmethod
    async def create(session, subscription: Subscription) -> Subscription:
        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)
        return subscription

    @staticmethod
    async def update(session, subscription: Subscription) -> Subscription:
        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)
        return subscription

    @staticmethod
    async def delete(session, subscription_id: UUID):
        await session.execute(
            delete(Subscription).where(Subscription.id == subscription_id)
        )
        await session.commit()

    @staticmethod
    def to_read_model(subscription: Subscription) -> SubscriptionRead:
        return SubscriptionRead(
            id=subscription.id,
            name=subscription.name,
            domain=subscription.domain,
            paywall=subscription.paywall,
            username=subscription.username,
        )

    @staticmethod
    async def delete_links_for_search_profile(
        session: AsyncSession, profile_id: UUID
    ) -> None:
        stmt = delete(SearchProfileSubscriptionLink).where(
            SearchProfileSubscriptionLink.search_profile_id == profile_id
        )
        await session.execute(stmt)


async def get_subscriptions_with_crawlers(
    crawler: CrawlerType = None,
) -> list[Subscription]:
    """Get all subscriptions that have crawlers enabled.
    This function retrieves all active subscriptions that have
    crawlers associated with them. If a specific crawler type is
    provided, it filters the subscriptions to only include those
    that have the specified crawler type in their crawlers list.

    Args:
        crawler (CrawlerType, optional): The type of crawler to filter by.
        Defaults to None.

    Returns:
        list[Subscription]: A list of Subscription objects that have crawlers.
    """
    async with async_session() as session:
        stmt = select(Subscription).where(
            Subscription.crawlers.isnot(None), Subscription.is_active.is_(True)
        )
        result = await session.execute(stmt)
        result = result.scalars().all()
        if crawler:
            result = [sub for sub in result if crawler.value in sub.crawlers]
        for subscription in result:
            subscription.crawlers = get_crawlers(subscription)
        return result


async def get_subscriptions_with_scrapers() -> list[Subscription]:
    """Get all subscriptions that have scrapers enabled.
    This function retrieves all active subscriptions that have a
    scraper. It also checks if the subscription has any articles
    that have not been scraped yet.

    Returns:
        list[Subscription]: A list of Subscription objects with the scraper
        class.
    """
    async with async_session() as session:
        stmt = (
            select(Subscription.id)
            .join(Article, Article.subscription_id == Subscription.id)
            .where(
                Subscription.scrapers.isnot(None),
                Article.status == "NEW",
                Subscription.is_active.is_(True),
            )
            .distinct()
        )
        result = await session.execute(stmt)
        ids = result.scalars().all()

        subscriptions = (
            (
                await session.execute(
                    select(Subscription).where(Subscription.id.in_(ids))
                )
            )
            .scalars()
            .all()
        )

        for subscription in subscriptions:
            subscription.scrapers = get_scraper(subscription)
        return subscriptions
