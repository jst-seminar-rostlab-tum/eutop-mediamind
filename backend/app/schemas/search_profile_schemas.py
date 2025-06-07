from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.subscription_schemas import SubscriptionSummary
from app.schemas.topic_schemas import (
    TopicCreateOrUpdateRequest,
    TopicResponse,
)

# --- Shared Base Models ---


class SearchProfileBase(BaseModel):
    name: str
    public: bool
    organization_emails: List[EmailStr]
    profile_emails: List[EmailStr]
    subscriptions: List[SubscriptionSummary]


# --- Request Models ---


class SearchProfileCreateRequest(SearchProfileBase):
    topics: List[TopicCreateOrUpdateRequest]


class SearchProfileUpdateRequest(SearchProfileBase):
    topics: List[TopicCreateOrUpdateRequest]


# --- Response Models ---


class SearchProfileDetailBase(BaseModel):
    id: UUID
    name: str
    public: bool
    organization_emails: List[EmailStr]
    profile_emails: List[EmailStr]
    editable: bool
    is_editable: bool
    owner: UUID
    is_owner: bool
    topics: List[TopicResponse]


class SearchProfileDetailResponse(SearchProfileDetailBase):
    subscriptions: List[SubscriptionSummary]
    new_articles_count: int
