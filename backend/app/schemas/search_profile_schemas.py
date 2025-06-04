from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class TopicUpdate(BaseModel):
    name: str
    keywords: List[str]


class SubscriptionUpdate(BaseModel):
    id: int
    name: str


class SearchProfileUpdateRequest(BaseModel):
    id: UUID
    name: str
    organization_emails: Optional[List[str]] = []
    profile_emails: Optional[List[str]] = []
    public: bool
    is_editable: Optional[bool] = True
    owner: UUID
    is_owner: Optional[bool] = False
    subscriptions: Optional[List[SubscriptionUpdate]] = []
    topics: Optional[List[TopicUpdate]] = []


class TopicOut(BaseModel):
    name: str
    keywords: List[str]


class TopicResponse(BaseModel):
    name: str
    keywords: List[str]


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
    topics: List[TopicResponse]
