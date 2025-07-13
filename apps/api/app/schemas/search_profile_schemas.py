from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.core.languages import Language
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
    language: str = Language.EN.value


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
    language: str = Language.EN.value
    topics: List[TopicResponse]


class SearchProfileDetailResponse(SearchProfileDetailBase):
    subscriptions: List[SubscriptionSummary]
    new_articles_count: int


class KeywordSuggestionTopic(BaseModel):
    topic_name: str
    keywords: List[str]


class KeywordSuggestionRequest(BaseModel):
    search_profile_name: str
    search_profile_language: str
    related_topics: List[KeywordSuggestionTopic]
    selected_topic: KeywordSuggestionTopic


class KeywordSuggestionResponse(BaseModel):
    suggestions: List[str]
