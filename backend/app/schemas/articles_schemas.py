from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import Match
from app.models.article import ArticleStatus


class ArticleOverviewItem(BaseModel):
    id: UUID
    title: str
    url: str
    author: str
    published_at: datetime
    language: str
    category: str
    summary: str | None
    sorting_order: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, match: Match) -> "ArticleOverviewItem":
        article = match.article
        return cls(
            id=article.id,
            title=article.title,
            url=article.url,
            author=article.author,
            published_at=article.published_at,
            language=article.language,
            category=article.category,
            summary=article.summary,
            sorting_order=match.sorting_order,
        )


class MatchArticleOverviewContent(BaseModel):
    article_url: str
    headline: dict[str, str]
    summary: dict[str, str]
    text: dict[str, str]
    image_urls: list[str]
    published: datetime
    crawled: datetime
    newspaper_id: UUID | None = None
    authors: list[str] | None = None
    categories: list[str] | None = None
    status: ArticleStatus | None = None


class MatchTopicItem(BaseModel):
    id: UUID
    name: str
    score: float
    keywords: list[str] | None = None


class MatchProfileInfo(BaseModel):
    id: UUID
    name: str


class MatchItem(BaseModel):
    id: UUID
    relevance: float
    topics: list[MatchTopicItem]
    article: MatchArticleOverviewContent


class ArticleOverviewResponse(BaseModel):
    matches: list[MatchItem]


class MatchDetailResponse(BaseModel):
    match_id: UUID
    topics: list[MatchTopicItem]
    search_profile: MatchProfileInfo | None
    article: MatchArticleOverviewContent

    model_config = ConfigDict(from_attributes=True)
