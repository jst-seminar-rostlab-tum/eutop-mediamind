from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.article import ArticleStatus


class MatchArticleOverviewContent(BaseModel):
    article_url: str
    headline: dict[str, str]
    summary: dict[str, str]
    text: dict[str | None, str | None]
    image_urls: List[str]
    published: datetime
    crawled: datetime
    newspaper_id: UUID | None = None
    authors: List[str] | None = None
    categories: List[str] | None = None
    status: ArticleStatus | None = None
    language: str | None = None


class MatchTopicItem(BaseModel):
    id: UUID
    name: str
    score: float
    keywords: List[str] | None = None


class MatchProfileInfo(BaseModel):
    id: UUID
    name: str


class MatchItem(BaseModel):
    id: UUID
    relevance: float
    topics: List[MatchTopicItem]
    article: MatchArticleOverviewContent


class ArticleOverviewResponse(BaseModel):
    matches: List[MatchItem]


class MatchDetailResponse(BaseModel):
    match_id: UUID
    topics: List[MatchTopicItem]
    search_profile: MatchProfileInfo | None
    article: MatchArticleOverviewContent
    entities: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
