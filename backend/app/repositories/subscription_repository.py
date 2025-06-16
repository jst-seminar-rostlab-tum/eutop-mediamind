from uuid import UUID

from sqlalchemy import delete, exists, select
from sqlalchemy.orm import aliased

from app.core.db import async_session
from app.models import Subscription
from app.models.associations import SearchProfileSubscriptionLink
from app.schemas.subscription_schemas import (
    SubscriptionSummary,
)


class SubscriptionsRepository:
    @staticmethod
    async def get_all_subscriptions_with_search_profile(
        search_profile_id: UUID,
    ) -> list[SubscriptionSummary]:
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
    async def get_all_subscriptions() -> list[SubscriptionSummary]:
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
