from uuid import UUID

from pydantic import BaseModel


class SubscriptionSummary(BaseModel):
    id: UUID
    name: str
    is_subscribed: bool


class SearchProfileSubscriptionLink(BaseModel):
    subscription_id: UUID


class SetSearchProfileSubscriptionsRequest(BaseModel):
    search_profile_id: UUID
    subscriptions: list[SearchProfileSubscriptionLink]
