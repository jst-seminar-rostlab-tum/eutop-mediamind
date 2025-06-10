from typing import List

from app.repositories.subscription_repository import get_all_subscriptions
from app.schemas.subscription_schemas import SubscriptionSummary


class SubscriptionService:
    @staticmethod
    async def get_all_subscriptions() -> List[SubscriptionSummary]:
        subscriptions = await get_all_subscriptions()
        return [
            SubscriptionSummary(
                id=sub.id,
                name=sub.name,
                is_subscribed=False,  # No search profile context
            )
            for sub in subscriptions
        ]
