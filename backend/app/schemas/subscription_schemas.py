from uuid import UUID

from pydantic import BaseModel


class SubscriptionSummary(BaseModel):
    id: UUID
    name: str
    is_subscribed: bool


class SetSearchProfileSubscriptionsRequest(BaseModel):
    search_profile_id: UUID
    subscriptions: list[SubscriptionSummary]


class SubscriptionCreateOrUpdate(BaseModel):
    name: str
    domain: str
    paywall: bool
    username: str
    password: str


class SubscriptionRead(BaseModel):
    id: UUID
    name: str
    domain: str
    paywall: bool
    username: str
