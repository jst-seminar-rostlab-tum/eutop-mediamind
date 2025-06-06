from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.topic_schemas import (
    TopicCreateRequest,
    TopicResponse,
    TopicUpdateRequest,
)


class SubscriptionUpdate(BaseModel):
    id: int
    name: str


class SearchProfileUpdateRequest(BaseModel):
    name: str
    public: bool
    organization_emails: list[EmailStr]
    profile_emails: list[EmailStr]
    topics: list[TopicUpdateRequest]


class SearchProfileCreateRequest(BaseModel):
    name: str
    public: bool
    organization_id: UUID
    organization_emails: List[EmailStr]
    profile_emails: List[EmailStr]
    topics: List[TopicCreateRequest]


class SearchProfileDetailResponseWithNewArticleCount(BaseModel):
    id: UUID
    name: str
    organization_emails: List[EmailStr]
    profile_emails: List[EmailStr]
    public: bool
    editable: bool
    is_editable: bool
    owner: UUID
    is_owner: bool
    topics: list[TopicResponse]
    new_articles_count: int


class SearchProfileDetailResponse(BaseModel):
    id: UUID
    name: str
    organization_emails: List[EmailStr]
    profile_emails: List[EmailStr]
    public: bool
    editable: bool
    is_editable: bool
    owner: UUID
    is_owner: bool
    topics: list[TopicResponse]

    model_config = ConfigDict(from_attributes=True)
