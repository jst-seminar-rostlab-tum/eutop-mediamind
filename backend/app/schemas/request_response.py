from datetime import date
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class FeedbackResponse(BaseModel):
    status: str


class MatchFilterRequest(BaseModel):
    startDate: date
    endDate: date
    sorting: Literal["DATE", "RELEVANCE"]
    searchTerm: Optional[str] = None
    topics: Optional[List[UUID]] = None
    subscriptions: Optional[List[UUID]] = None
