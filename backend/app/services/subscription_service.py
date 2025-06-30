from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, select

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
            subscription = Subscription(
                name=data.name,
                domain=data.domain,
                paywall=data.paywall,
                username=data.username,
                secrets=data.password,
            )
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

            if data.domain != subscription.domain:
                subscription.domain = data.domain
            if data.paywall != subscription.paywall:
                subscription.paywall = data.paywall
            if data.name != subscription.name:
                subscription.name = data.name
            if data.username != subscription.username:
                subscription.username = data.username
            if data.password is not None:
                subscription.secrets = data.password

            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)
            return subscription

    @staticmethod
    async def delete(subscription_id: UUID) -> None:
        async with async_session() as session:
            await session.execute(
                delete(Subscription).where(Subscription.id == subscription_id)
            )
            await session.commit()

    @staticmethod
    async def get(subscription_id: UUID) -> SubscriptionRead:
        async with async_session() as session:
            stmt = select(Subscription).where(
                Subscription.id == subscription_id
            )
            result = await session.execute(stmt)
            subscription = result.scalar_one_or_none()
            return SubscriptionRead(
                id=subscription.id,
                name=subscription.name,
                domain=subscription.domain,
                paywall=subscription.paywall,
                username=subscription.username,
            )
