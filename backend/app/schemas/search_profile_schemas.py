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
    can_edit_user_ids: List[UUID] = []
    can_read_user_ids: List[UUID] = []
    subscriptions: List[SubscriptionSummary]
    owner_id: UUID
    language: str = "en"


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
    can_read_user_ids: List[UUID]
    is_reader: bool
    can_edit_user_ids: List[UUID]
    is_editor: bool
    owner_id: UUID
    is_owner: bool
    language: str = "en"
    topics: List[TopicResponse]


class SearchProfileDetailResponse(SearchProfileDetailBase):
    subscriptions: List[SubscriptionSummary]
    new_articles_count: int


class KeywordSuggestionResponse(BaseModel):
    suggestions: List[str]

    def to_dict(self):
        return {"keyword_suggestions": self.suggestions}
