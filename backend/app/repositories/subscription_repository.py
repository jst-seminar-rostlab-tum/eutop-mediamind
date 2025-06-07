from uuid import UUID

from sqlalchemy import delete, exists, select
from sqlalchemy.orm import aliased

from app.core.db import async_session
from app.models import Subscription
from app.models.associations import SearchProfileSubscriptionLink
from app.schemas.subscription_schemas import (
    SubscriptionSummary,
)


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


async def get_all_subscriptions() -> list[SubscriptionSummary]:
    async with async_session() as session:
        stmt = select(Subscription.id, Subscription.name)
        result = await session.execute(stmt)

        return [
            SubscriptionSummary(id=row.id, name=row.name, is_subscribed=False)
            for row in result
        ]


async def set_subscriptions_for_profile(
    profile_id: UUID, subscription_ids: list[UUID]
) -> None:
    async with async_session() as session:
        # Delete existing links
        await session.execute(
            delete(SearchProfileSubscriptionLink).where(
                SearchProfileSubscriptionLink.search_profile_id == profile_id
            )
        )

        # Add new links
        objects = [
            SearchProfileSubscriptionLink(
                search_profile_id=profile_id, subscription_id=sub_id
            )
            for sub_id in subscription_ids
        ]
        session.add_all(objects)
        await session.commit()
