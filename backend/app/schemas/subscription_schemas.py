from uuid import UUID

from pydantic import BaseModel


class SubscriptionSummary(BaseModel):
    id: UUID
    name: str
    is_subscribed: bool


class SetSearchProfileSubscriptionsRequest(BaseModel):
    search_profile_id: UUID
    subscriptions: list[SubscriptionSummary]


class SetOrganizationSubscriptionsRequest(BaseModel):
    organization_id: UUID
    subscriptions: list[SubscriptionSummary]
