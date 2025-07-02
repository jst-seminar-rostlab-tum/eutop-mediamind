from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.core.db import async_session
from app.models import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription_schemas import (
    SubscriptionCreateOrUpdate,
    SubscriptionRead,
    SubscriptionSummary,
)


class SubscriptionService:
    @staticmethod
    async def get_all_subscriptions() -> List[SubscriptionSummary]:
        subscriptions = await SubscriptionRepository.get_all()
        return [
            SubscriptionSummary(
                id=sub.id,
                name=sub.name,
                is_subscribed=False,  # No search profile context
            )
            for sub in subscriptions
        ]

    @staticmethod
    async def create(data: SubscriptionCreateOrUpdate) -> SubscriptionRead:
        async with async_session() as session:
            subscription = Subscription(
                name=data.name,
                domain=data.domain,
                paywall=data.paywall,
            )
            subscription.username = data.username
            subscription.secrets = data.password
            created = await SubscriptionRepository.create(
                session, subscription
            )
            return SubscriptionRepository.to_read_model(created)

    @staticmethod
    async def update(
        subscription_id: UUID, data: SubscriptionCreateOrUpdate
    ) -> SubscriptionRead:
        async with async_session() as session:
            subscription = await SubscriptionRepository.get_by_id(
                session, subscription_id
            )
            if not subscription:
                raise HTTPException(
                    status_code=404, detail="Subscription not found"
                )

            # Update logic
            subscription.domain = data.domain
            subscription.paywall = data.paywall
            subscription.name = data.name
            subscription.username = data.username
            if data.password is not None:
                subscription.secrets = data.password

            updated = await SubscriptionRepository.update(
                session, subscription
            )
            return SubscriptionRepository.to_read_model(updated)

    @staticmethod
    async def delete(subscription_id: UUID) -> None:
        async with async_session() as session:
            await SubscriptionRepository.delete(session, subscription_id)

    @staticmethod
    async def get(subscription_id: UUID) -> SubscriptionRead:
        async with async_session() as session:
            subscription = await SubscriptionRepository.get_by_id(
                session, subscription_id
            )
            if not subscription:
                raise HTTPException(
                    status_code=404, detail="Subscription not found"
                )
            return SubscriptionRepository.to_read_model(subscription)
