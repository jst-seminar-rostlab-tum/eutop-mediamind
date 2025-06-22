from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.subscription_schemas import SubscriptionSummary
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest, TopicResponse

# --- Shared Base Models ---


class SearchProfileBase(BaseModel):
    name: str
    is_public: bool
    organization_emails: List[EmailStr] = []
    profile_emails: List[EmailStr] = []
    can_edit: List[UUID] = []
    can_read: List[UUID] = []
    subscriptions: List[SubscriptionSummary]
    owner_id: UUID


# --- Request Models ---


class SearchProfileCreateRequest(SearchProfileBase):
    topics: List[TopicCreateOrUpdateRequest]


class SearchProfileUpdateRequest(SearchProfileBase):
    topics: List[TopicCreateOrUpdateRequest]


# --- Response Models ---


class SearchProfileDetailBase(BaseModel):
    id: UUID
    name: str
    is_public: bool
    organization_emails: List[EmailStr]
    profile_emails: List[EmailStr]
    can_read: bool
    can_edit: bool
    owner_id: UUID
    is_owner: bool
    topics: List[TopicResponse]


class SearchProfileDetailResponse(SearchProfileDetailBase):
    subscriptions: List[SubscriptionSummary]
    new_articles_count: int


class KeywordSuggestionResponse(BaseModel):
    suggestions: List[str]

    def to_dict(self):
        return {"keyword_suggestions": self.suggestions}
