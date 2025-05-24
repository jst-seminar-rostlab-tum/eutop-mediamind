from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


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
    editable: Optional[bool] = True
    is_editable: Optional[bool] = True
    owner: UUID
    is_owner: Optional[bool] = False
    subscriptions: Optional[List[SubscriptionUpdate]] = []
    topics: Optional[List[TopicUpdate]] = []

class TopicOut(BaseModel):
    name: str
    keywords: List[str]


class SearchProfileDetailResponse(BaseModel):
    id: UUID
    name: str
    organization_emails: List[str]
    profile_emails: List[str]
    public: bool
    editable: bool
    is_editable: bool
    owner: UUID
    is_owner: bool
    topics: List[TopicOut]

    class Config:
        orm_mode = True