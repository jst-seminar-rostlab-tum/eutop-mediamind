from uuid import UUID

from sqlalchemy import delete, select

from app.core.db import async_session
from app.models import Subscription
from app.schemas.subscription_schemas import (
    SearchProfileSubscriptionLink,
    SubscriptionSummary,
)


async def get_available_subscriptions() -> list[SubscriptionSummary]:
    async with async_session() as session:
        stmt = select(Subscription.id, Subscription.name)
        result = await session.exec(stmt)
        return [
            SubscriptionSummary(id=row.id, name=row.name) for row in result
        ]


async def set_subscriptions_for_profile(
    profile_id: UUID, subscription_ids: list[UUID]
) -> None:
    async with async_session() as session:
        # Delete existing links
        await session.exec(
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
