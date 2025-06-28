from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.core.db import async_session
from app.models import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription_schemas import (
    SubscriptionCreateOrUpdate,
    SubscriptionSummary,
)


class SubscriptionService:
    @staticmethod
    async def get_all_subscriptions() -> List[SubscriptionSummary]:
        subscriptions = await SubscriptionRepository.get_all_subscriptions()
        return [
            SubscriptionSummary(
                id=sub.id,
                name=sub.name,
                is_subscribed=False,  # No search profile context
            )
            for sub in subscriptions
        ]

    @staticmethod
    async def create(data: SubscriptionCreateOrUpdate) -> Subscription:
        async with async_session() as session:
            subscription = Subscription(**data.model_dump(exclude_unset=True))
            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)
            return subscription

    @staticmethod
    async def update(
        subscription_id: UUID, data: SubscriptionCreateOrUpdate
    ) -> Subscription:
        async with async_session() as session:
            subscription = await session.get(Subscription, subscription_id)
            if not subscription:
                raise HTTPException(
                    status_code=404, detail="Subscription not found"
                )

            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(subscription, key, value)

            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)
            return subscription

    @staticmethod
    async def delete(subscription_id: UUID) -> None:
        async with async_session() as session:
            subscription = await session.get(Subscription, subscription_id)
            if not subscription:
                raise HTTPException(
                    status_code=404, detail="Subscription not found"
                )

            await session.delete(subscription)
            await session.commit()
