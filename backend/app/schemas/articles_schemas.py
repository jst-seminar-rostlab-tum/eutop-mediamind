from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import Match


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


class ArticleOverviewResponse(BaseModel):
    search_profile_id: UUID
    articles: list[ArticleOverviewItem]


class MatchDetailResponse(BaseModel):
    match_id: UUID
    comment: str | None
    sorting_order: int

    article_id: UUID
    title: str
    url: str
    author: str
    published_at: datetime
    language: str
    category: str
    summary: str | None
    content: str | None

    model_config = ConfigDict(from_attributes=True)
